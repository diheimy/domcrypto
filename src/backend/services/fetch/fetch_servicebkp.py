import asyncio
import logging
import ccxt.async_support as ccxt
from src.backend.services.funding.funding_fetcher import FundingFetcher

logger = logging.getLogger("FetchService")

class FetchService:
    def __init__(self):
        self.exchanges = {
            "mexc": ccxt.mexc({'enableRateLimit': True}),
            "gate": ccxt.gateio({'enableRateLimit': True}),
            "bitget": ccxt.bitget({'enableRateLimit': True}),
            # "bingx": ccxt.bingx({'enableRateLimit': True}), # 🔴 Mantido Off
        }
        self.funding_fetcher = FundingFetcher(self.exchanges)

    async def fetch_all(self):
        tasks = []
        for name, exch in self.exchanges.items():
            tasks.append(self._fetch_exchange(name, exch))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        spot_data = {}
        futures_data = {}
        
        for res in results:
            if isinstance(res, tuple) and len(res) == 3:
                name, s_tickers, f_tickers = res
                if s_tickers: spot_data[name] = s_tickers
                if f_tickers: futures_data[name] = f_tickers
                
        return spot_data, futures_data

    async def _fetch_exchange(self, name, exch):
        try:
            # [CORREÇÃO] Carregar mercados para ter metadados precisos (type: swap/spot)
            if not exch.markets:
                await exch.load_markets()

            tickers = await exch.fetch_tickers()
            
            spot = {}
            futures = {}
            
            for symbol, ticker in tickers.items():
                market = exch.markets.get(symbol)
                
                # Heurística Robusta baseada em Metadados da Exchange
                is_future = False
                if market:
                    # Verifica tipos comuns de futuros: swap, future
                    if market.get('type') in ('swap', 'future') or market.get('linear') or market.get('inverse'):
                        is_future = True
                    # Fallback para string parsing se metadado falhar ou não existir
                    elif ':' in symbol or 'PERP' in symbol:
                        is_future = True
                else:
                    # Fallback legado se o mercado não estiver carregado
                    if ':' in symbol or 'PERP' in symbol:
                        is_future = True

                if is_future:
                    futures[symbol] = ticker
                else:
                    spot[symbol] = ticker
                    
            return name, spot, futures
        except Exception as e:
            logger.error(f"Erro fetch {name}: {e}")
            return name, {}, {}

    async def close_all(self):
        for exch in self.exchanges.values():
            await exch.close()