from typing import List, Dict, Any
from src.backend.pipeline.opportunity_builder import OpportunityBuilder
from src.backend.services.paper.paper_trading_service import PaperTradingService

class BacktestEngine:
    """
    Motor de Replay Determinístico.
    Simula a passagem do tempo injetando frames históricos no Pipeline.
    """

    @staticmethod
    def replay(frames: List[Dict[str, Any]]):
        """
        Executa o pipeline completo para cada frame histórico.
        """
        print("▶️ Iniciando Replay de Mercado...")
        
        count = 0
        total = len(frames)
        
        for frame in frames:
            count += 1
            if count % 100 == 0:
                print(f"   Processando frame {count}/{total}...")

            # 1. Constrói oportunidades (Usa as mesmas regras do Live: Score, Spread Líquido, etc)
            opportunities = OpportunityBuilder.build_batch(frame)

            # 2. Executa o motor de trading (Abre/Fecha posições, Stop Loss, Take Profit)
            # O Service não sabe que está rodando em backtest.
            PaperTradingService.process_batch(opportunities)

        print("⏹️ Replay finalizado.")