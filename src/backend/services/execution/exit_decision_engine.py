from typing import List, Tuple
from datetime import datetime
from src.backend.services.execution.exit_models.base_exit_model import ExitModel

class ExitDecisionEngine:
    """
    Engine que orquestra multiplos modelos de saida.
    O primeiro modelo que retornar True encerra a operacao (Fail-Fast).
    """

    def __init__(self, models: List[ExitModel]):
        self.models = models

    def evaluate(
        self,
        snapshot,
        now: datetime,
        current_spot_price: float,
        current_futures_price: float
    ) -> Tuple[bool, str]:
        
        for model in self.models:
            should_close, reason = model.evaluate(
                snapshot,
                now,
                current_spot_price,
                current_futures_price
            )
            
            if should_close:
                return True, reason

        return False, "HOLD_ALL_MODELS"
