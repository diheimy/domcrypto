from abc import ABC, abstractmethod
from typing import Tuple
from datetime import datetime
from src.backend.services.persistence.models_paper import PaperTradeSnapshot

class ExitModel(ABC):
    @abstractmethod
    def evaluate(
        self,
        snapshot: PaperTradeSnapshot,
        now: datetime,
        current_spot_price: float,
        current_futures_price: float
    ) -> Tuple[bool, str]:
        pass
