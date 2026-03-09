import logging
from typing import List, Tuple
import ccxt.async_support as ccxt

from src.backend.services.market_data.orderbook_depth_state import OrderBookDepthState

logger = logging.getLogger("OrderBookFetcher")


class OrderBookFetcher:
    """
    Sensor de Order Book.
    Busca profundidade e atualiza o estado local.
    """

    def __init__(
        self,
        exchange_name: str,
        symbols: List[str],
        depth: int = 5
    ):
        self.exchange_name = exchange_name.lower()
        self.symbols = symbols
        self.depth = depth

        self.exchange = self._init_exchange()

        # Estado por símbolo
        self.states = {
            symbol: OrderBookDepthState(symbol)
            for symbol in symbols
        }

    def _init_exchange(self):
        if not hasattr(ccxt, self.exchange_name):
            raise ValueError(f"Exchange não suportada: {self.exchange_name}")

        exchange_class = getattr(ccxt, self.exchange_name)
        return exchange_class({"enableRateLimit": True})

    async def fetch_once(self):
        """
        Faz uma leitura única do order book para todos os símbolos.
        """
        for symbol in self.symbols:
            try:
                orderbook = await self.exchange.fetch_order_book(
                    symbol,
                    limit=self.depth
                )

                bids = orderbook.get("bids", [])
                asks = orderbook.get("asks", [])

                bid_liq, ask_liq = self._calculate_liquidity(bids, asks)

                self.states[symbol].update(
                    bid_liq_usd=bid_liq,
                    ask_liq_usd=ask_liq
                )

            except Exception as e:
                logger.warning(
                    f"Erro ao buscar order book {symbol} ({self.exchange_name}): {e}"
                )

    def _calculate_liquidity(
        self,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ) -> tuple[float, float]:
        """
        Converte níveis do livro em liquidez financeira (USD).
        """
        bid_liq = sum(price * amount for price, amount in bids)
        ask_liq = sum(price * amount for price, amount in asks)
        return bid_liq, ask_liq

    async def close(self):
        await self.exchange.close()
