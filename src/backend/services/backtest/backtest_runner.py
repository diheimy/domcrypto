from src.backend.services.backtest.backtest_context import BacktestContext
from src.backend.services.backtest.backtest_loader import BacktestLoader
from src.backend.services.backtest.backtest_engine import BacktestEngine
from src.backend.services.analytics.equity.equity_curve_service import EquityCurveService
from src.backend.services.backtest.backtest_result import BacktestResult

class BacktestRunner:
    """
    Fachada (Facade) para execução simplificada de backtests.
    """

    @staticmethod
    def run(dataset_path: str, initial_capital: float = 1000.0) -> BacktestResult:
        print(f"\n🧪 INICIANDO BACKTEST [Capital Inicial: ${initial_capital}]")
        print("="*60)

        # 1. Resetar o ambiente (Garante pureza do teste)
        BacktestContext.reset()

        # 2. Carregar dados
        frames = BacktestLoader.load_from_json(dataset_path)

        # 3. Executar Replay
        BacktestEngine.replay(frames)

        # 4. Gerar Analytics (Usa o mesmo serviço da API)
        report = EquityCurveService.generate_report(initial_capital)

        # 5. Empacotar Resultado
        result = BacktestResult(
            equity_report=report,
            total_trades=report["total_trades"],
            win_rate=report["win_rate"],
            max_drawdown_pct=report["max_drawdown_pct"],
            final_capital=report["final_capital"],
            total_roi_pct=report["total_roi_pct"]
        )
        
        print("="*60)
        print("🏁 BACKTEST CONCLUÍDO")
        return result