import logging
import asyncio
import ccxt.async_support as ccxt
from src.backend.services.funding.funding_state import FundingState

logger = logging.getLogger("FundingFetcher")

class FundingFetcher:
    """
    F8.2 — Funding Fetcher Real (CCXT) - Institutional Refined
    Busca funding real com normalização de ID (Mapper), rate limit lock e filtros de anomalia.
    """

    def __init__(self, exchanges: dict):
        """
        exchanges: dict de instâncias CCXT (injetado pelo FetchService)
        """
        self.exchanges = exchanges
        self.state = FundingState(ttl_seconds=300) # 5 min cache
        
        # [BLINDAGEM] Lock Institucional (Asyncio)
        self._lock = asyncio.Lock()

    def _map_symbol(self, exchange_name: str, symbol: str) -> str:
        """
        Mapeia símbolos genéricos (BTC/USDT, BTCUSDT) para o formato específico 
        de contrato perpétuo de cada exchange.
        """
        # Normalização básica
        s = symbol.upper().replace("/", "").replace("_", "").replace("-", "")
        # Remove sufixos comuns que possam vir do builder
        base = s.split(":")[0].replace("PERP", "").replace("SWAP", "")
        
        # Lógica Específica por Exchange
        if exchange_name == "mexc":
            # MEXC Futures geralmente usa formato BTC_USDT
            # Se for SWAP, ignora pois é inválido
            if "SWAP" in base: return None
            return f"{base}_USDT" 
            
        elif exchange_name == "gate":
            # Gate usa BTC_USDT
            return f"{base}_USDT"
            
        elif exchange_name == "bitget":
            # Bitget usa BTCUSDT_UMCBL (ou similar, dependendo da API v1/v2)
            # CCXT geralmente normaliza, mas tentamos o padrão mais comum
            return f"{base}USDT_UMCBL"

        elif exchange_name == "bingx":
            # BingX usa BTC-USDT
            return f"{base}-USDT"

        # Padrão Genérico (Fallback)
        return f"{base}/USDT:USDT" # Padrão CCXT Unified

    async def fetch(self, exchange_name: str, symbol: str):
        if not exchange_name or not symbol:
            return None

        # Normaliza nome da exchange
        clean_exch_name = exchange_name.replace("_futures", "").lower()

        # Blindagem contra concorrência e Rate Limit
        async with self._lock:
            # 1. Verifica Cache (Double-check dentro do lock)
            cached = self.state.get(clean_exch_name, symbol)
            if cached is not None:
                return cached

            exchange = self.exchanges.get(clean_exch_name)
            if not exchange:
                return None

            # 2. Mapeamento de Símbolo (FIX CRÍTICO)
            # Transforma "BTC/USDT" em "BTC_USDT" (ou o que a exchange exigir)
            request_symbol = self._map_symbol(clean_exch_name, symbol)
            
            if not request_symbol:
                # Se não conseguiu mapear (ex: símbolo inválido), retorna None sem erro
                return None

            try:
                # 3. Chamada de Rede (CCXT)
                # fetch_funding_rate espera o símbolo do contrato
                res = await exchange.fetch_funding_rate(request_symbol)
                
                rate = res.get("fundingRate")
                if rate is None:
                    return None

                # Converte para Porcentagem
                rate_pct = rate * 100

                # [BLINDAGEM] Filtro de Anomalia (Sanity Check)
                # Funding > 1% (8h) é extremamente raro (erro de dado ou flash crash).
                if abs(rate_pct) > 1.0:
                    logger.warning(f"⚠️ Funding anômalo ignorado [{clean_exch_name} {symbol}]: {rate_pct:.4f}%")
                    return None

                # 4. Salva no Cache (usando o símbolo ORIGINAL como chave para consistência)
                self.state.set(clean_exch_name, symbol, rate_pct)
                
                return rate_pct

            except (ccxt.BadSymbol, ccxt.BadRequest) as e:
                # Log Level: Debug para erro de símbolo (comum, não crítico)
                # "Contract does not exist" cai aqui
                logger.debug(f"ℹ️ Funding n/a [{clean_exch_name}]: Contrato {request_symbol} não encontrado.")
                return None
                
            except ccxt.NetworkError as e:
                # Log Level: Warning para rede (pode ser transitório)
                logger.warning(f"⚠️ Erro de Rede Funding [{clean_exch_name}]: {e}")
                return None
                
            except Exception as e:
                # Log Level: Error apenas para falhas de lógica/código
                # Filtrar mensagens de erro comuns de API para não poluir
                msg = str(e).lower()
                if "contract does not exist" in msg or "instrument id does not exist" in msg:
                    logger.debug(f"ℹ️ Funding n/a [{clean_exch_name}]: {msg}")
                else:
                    logger.error(f"❌ Erro Funding Inesperado [{clean_exch_name} {symbol}]: {e}")
                return None