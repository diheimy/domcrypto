from abc import ABC, abstractmethod
from src.backend.services.execution.execution_result import ExecutionResult

class BaseExecutionEngine(ABC):
    """
    Interface padrão para execução de trades.
    Qualquer engine (Paper, Binance, Bybit) deve herdar daqui.
    """

    @abstractmethod
    def execute_entry(self, trade) -> ExecutionResult:
        """Executa a entrada (Compra Spot + Venda Futuros)"""
        pass

    @abstractmethod
    def execute_exit(self, trade) -> ExecutionResult:
        """Executa a saída (Venda Spot + Compra Futuros)"""
        pass