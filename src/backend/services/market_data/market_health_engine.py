import logging
from typing import List, Dict

from src.backend.models.opportunity import Opportunity
from src.backend.services.market_data.orderbook_depth_state import OrderBookDepthState
from src.backend.services.market_data.orderbook_fetcher import OrderBookFetcher

logger = logging.getLogger("MarketHealthEngine")

class MarketHealthEngine:
    """
    Maestro da Etapa 2.
    Coordena: Fetcher -> State -> Health Metrics.
    """

    def __init__(
        self,
        depth_state: OrderBookDepthState,
        min_liquidity_usd: float = 50_000,
        imbalance_threshold: float = 0.6
    ):
        self.state = depth_state
        self.fetcher = OrderBookFetcher(self.state) # Injeta o state no fetcher
        self.min_liquidity_usd = min_liquidity_usd
        self.imbalance_threshold = imbalance_threshold

    async def process_batch(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """
        Fluxo principal:
        1. Identifica símbolos.
        2. Atualiza dados (IO).
        3. Avalia saúde (CPU).
        """
        if not opportunities:
            return []

        # 1. Identificar símbolos únicos
        symbols = list(set([op.symbol for op in opportunities]))

        # 2. Atualizar Sensores (Através do OrderBookFetcher)
        await self.fetcher.fetch_and_update(symbols)

        # 3. Avaliar Saúde
        for op in opportunities:
            op.health = self._evaluate_single(op)

        return opportunities

    def _evaluate_single(self, op: Opportunity) -> Dict[str, float | bool]:
        """
        Consulta o State e aplica regras de saúde.
        """
        # Correção: Usar .get() do State
        spot_data = self.state.get(op.exchange_spot, op.symbol)
        fut_data = self.state.get(op.exchange_futures, op.symbol)

        if not spot_data or not fut_data:
            return self._unhealthy("no_data")

        # Dados extraídos do dicionário
        spot_bid = spot_data["bid_usd"]
        spot_ask = spot_data["ask_usd"]
        fut_bid = fut_data["bid_usd"]
        fut_ask = fut_data["ask_usd"]

        # Lógica de Imbalance e Liquidez
        total_liq = spot_bid + spot_ask + fut_bid + fut_ask

        if total_liq <= 0:
            return self._unhealthy("zero_liquidity")

        total_bids = spot_bid + fut_bid
        total_asks = spot_ask + fut_ask
        imbalance = abs(total_bids - total_asks) / total_liq

        healthy = (
            total_liq >= self.min_liquidity_usd
            and imbalance <= self.imbalance_threshold
        )

        return {
            "healthy": healthy,
            "total_liquidity_usd": float(total_liq),
            "imbalance": round(float(imbalance), 4),
            "updated_at": spot_data["timestamp"]
        }

    def _unhealthy(self, reason: str) -> Dict[str, float | bool | str]:
        return {
            "healthy": False,
            "reason": reason,
            "total_liquidity_usd": 0.0,
            "imbalance": 1.0
        }