from enum import Enum
from typing import Optional, Dict, Any
from src.backend.models.opportunity import Opportunity

class SpreadDirection(str, Enum):
    SPOT_TO_FUTURES = "spot_to_futures"  # Contango (Normal) -> Compra Spot, Vende Futuro
    FUTURES_TO_SPOT = "futures_to_spot"  # Backwardation (Invertido) -> Vende Spot, Compra Futuro

class SpreadEngine:
    """
    Responsável por calcular a magnitude e a direção do spread.
    Normaliza o spread para valor absoluto e usa tags para indicar direção.
    """

    @staticmethod
    def calculate(spot_price: float, futures_price: float) -> Optional[Dict[str, Any]]:
        """
        Retorna spread absoluto e direção.
        """
        if spot_price <= 0 or futures_price <= 0:
            return None

        # Cálculo matemático bruto
        raw_spread = ((futures_price - spot_price) / spot_price) * 100

        # Definição de direção e magnitude
        if raw_spread >= 0:
            direction = SpreadDirection.SPOT_TO_FUTURES
            abs_spread = raw_spread
        else:
            direction = SpreadDirection.FUTURES_TO_SPOT
            abs_spread = abs(raw_spread)

        return {
            "spread_pct": abs_spread,
            "direction": direction,
            "raw_spread": raw_spread # Mantemos o raw caso algum debug precise
        }

    @staticmethod
    def enrich(op: Opportunity) -> Opportunity:
        """
        Aplica a lógica de spread sobre a oportunidade, modificando-a in-place.
        """
        result = SpreadEngine.calculate(
            spot_price=op.spot_price,
            futures_price=op.futures_price
        )

        if not result:
            return op

        # Atualiza para Spread Absoluto (Magnitude da oportunidade)
        op.spread_pct = result["spread_pct"]
        
        # Injeta a direção nas tags (Metadado para UI e Executor)
        direction_tag = result["direction"].value
        if direction_tag not in op.tags:
            op.tags.append(direction_tag)

        return op