import ccxt.async_support as ccxt
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("ExchangeFetcher")

class ExchangeFetcher:
    def __init__(self):
        self.exchanges = {}
        self.initialized = False
        
        # Definição das conexões
        self.configs = [
            {'id': 'mexc_spot', 'lib': 'mexc', 'type': 'spot'},
            {'id': 'mexc_futures', 'lib': 'mexc', 'type': 'swap'},
            {'id': 'gate_spot', 'lib': 'gate', 'type': 'spot'},
            {'id': 'gate_futures', 'lib': 'gate', 'type': 'swap'},
            {'id': 'bitget_spot', 'lib': 'bitget', 'type': 'spot'},
            {'id': 'bitget_futures', 'lib': 'bitget', 'type': 'swap'},
            {'id': 'bingx_spot', 'lib': 'bingx', 'type': 'spot'},
            {'id': 'bingx_futures', 'lib': 'bingx', 'type': 'swap'},
        ]

    async def _init_exchanges(self):
        """Inicializa conexões apenas uma vez (Singleton Pattern interno)"""
        if self.initialized: return

        logger.info("🔌 Inicializando conexões globais com Exchanges...")
        
        for cfg in self.configs:
            try:
                exchange_class = getattr(ccxt, cfg['lib'])
                options = {'defaultType': cfg['type']}
                
                if cfg['lib'] == 'mexc':
                    options['adjustForTimeDifference'] = True
                
                # Instancia exchange
                exchange = exchange_class({
                    'enableRateLimit': True,
                    'options': options
                })
                
                self.exchanges[cfg['id']] = exchange
                
            except Exception as e:
                logger.error(f"❌ Falha ao carregar {cfg['id']}: {e}")

        self.initialized = True

    async def fetch_all(self) -> Dict[str, Any]:
        """Busca tickers de todas as corretoras em paralelo."""
        await self._init_exchanges()

        tasks = []
        ids = []

        for ex_id, exchange in self.exchanges.items():
            tasks.append(self._safe_fetch_tickers(exchange))
            ids.append(ex_id)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        raw_data = {}
        for ex_id, res in zip(ids, results):
            if isinstance(res, Exception):
                # logger.warning(f"Erro em {ex_id}: {res}")
                pass
            elif res:
                raw_data[ex_id] = res
        
        return raw_data

    async def _safe_fetch_tickers(self, exchange):
        try:
            return await exchange.fetch_tickers()
        except Exception:
            return None

    async def close_all(self):
        """Fecha todas as conexões abertas."""
        logger.info("🛑 Fechando conexões com exchanges...")
        for name, exchange in self.exchanges.items():
            try:
                await exchange.close()
            except Exception as e:
                logger.error(f"Erro ao fechar {name}: {e}")
        self.exchanges.clear()
        self.initialized = False