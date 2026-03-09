import asyncio
import logging

import ccxt.async_support as ccxt

from src.backend.services.funding.funding_fetcher import FundingFetcher

logger = logging.getLogger("FetchService")


class FetchService:
    """
    F1 — Market Data

    IMPORTANT:
    Muitos conectores CCXT só retornam tickers de *spot* por padrão.
    Para obter tickers de *swap/futures* de forma consistente, mantemos
    DUAS instâncias por exchange:
      - spot:   options.defaultType='spot'
      - futures:options.defaultType='swap'

    Isso evita Raw=0 causado por futures_data vazio.
    """

    def __init__(self):
        # Instâncias Spot
        self.exchanges_spot = {
            "mexc": ccxt.mexc({"enableRateLimit": True, "options": {"defaultType": "spot"}}),
            "gate": ccxt.gateio({"enableRateLimit": True, "options": {"defaultType": "spot"}}),
            "bitget": ccxt.bitget({"enableRateLimit": True, "options": {"defaultType": "spot"}}),
            # "bingx": ccxt.bingx({'enableRateLimit': True, 'options': {'defaultType': 'spot'}}),  # mantido off
        }

        # Instâncias Futures/Swap
        self.exchanges_futures = {
            "mexc": ccxt.mexc({"enableRateLimit": True, "options": {"defaultType": "swap"}}),
            "gate": ccxt.gateio({"enableRateLimit": True, "options": {"defaultType": "swap"}}),
            "bitget": ccxt.bitget({"enableRateLimit": True, "options": {"defaultType": "swap"}}),
            # "bingx": ccxt.bingx({'enableRateLimit': True, 'options': {'defaultType': 'swap'}}),
        }

        # Funding deve consultar a instância de futures (quando disponível)
        self.funding_fetcher = FundingFetcher(self.exchanges_futures)

    async def fetch_all(self):
        tasks = []
        for name in self.exchanges_spot.keys():
            tasks.append(self._fetch_exchange(name))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        spot_data = {}
        futures_data = {}

        for res in results:
            if isinstance(res, tuple) and len(res) == 3:
                name, s_tickers, f_tickers = res
                if s_tickers:
                    spot_data[name] = s_tickers
                if f_tickers:
                    futures_data[name] = f_tickers

        # Telemetria básica (ajuda a diagnosticar Raw=0)
        total_spot = sum(len(x) for x in spot_data.values())
        total_fut = sum(len(x) for x in futures_data.values())
        logger.info(f"📥 FETCH SUMMARY: spot={total_spot} futures={total_fut} exchanges={list(self.exchanges_spot.keys())}")

        return spot_data, futures_data

    async def _fetch_exchange(self, name: str):
        spot_ex = self.exchanges_spot.get(name)
        fut_ex = self.exchanges_futures.get(name)

        spot = {}
        futures = {}

        # Spot
        try:
            if spot_ex and not spot_ex.markets:
                await spot_ex.load_markets()
            if spot_ex:
                spot = await spot_ex.fetch_tickers()
        except Exception as e:
            logger.error(f"Erro fetch SPOT {name}: {e}")
            spot = {}

        # Futures/Swap
        try:
            if fut_ex and not fut_ex.markets:
                await fut_ex.load_markets()
            if fut_ex:
                futures = await fut_ex.fetch_tickers()
        except Exception as e:
            # Não derruba o ciclo: apenas loga e segue (isso explica Raw=0)
            logger.warning(f"⚠️ Futures tickers indisponíveis para {name}: {e}")
            futures = {}

        # Se o CCXT retornar None (raríssimo), normalize para dict vazio
        if spot is None:
            spot = {}
        if futures is None:
            futures = {}

        logger.info(f"📌 FETCH {name}: spot={len(spot)} futures={len(futures)}")
        return name, spot, futures

    async def close_all(self):
        for exch in list(self.exchanges_spot.values()) + list(self.exchanges_futures.values()):
            try:
                await exch.close()
            except Exception:
                pass
