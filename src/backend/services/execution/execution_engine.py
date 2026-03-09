from datetime import datetime
from src.backend.services.execution.order_intent import OrderIntent
from src.backend.services.execution.execution_plan import ExecutionPlanBuilder

class ExecutionEngine:
    """
    F7.4 - Motor de Execução Institucional.
    Executa ordens fatiadas apenas sob aprovação do F6.
    """
    def __init__(self, router_map, portfolio_state):
        self.router_map = router_map  # Mapeamento de instâncias CCXT
        self.portfolio = portfolio_state # Estado de Risco Global

    async def execute(self, op):
        # 1. RESPEITO ABSOLUTO À GOVERNANÇA (F6)
        if getattr(op, 'risk_decision', 'BLOCKED') != "APPROVED":
            return None

        # 2. Fatiamento F7.2 (Slicing)
        plan = ExecutionPlanBuilder.build(op)
        executed_usd = 0.0
        
        # Recupera o roteador correto para a exchange
        router = self.router_map.get(op.exchange_spot)
        
        # Nota: Se router for None (modo simulação), ainda processamos o loop 
        # para simular os slices, ou retornamos None dependendo da configuração.
        # Aqui, assumimos simulação se não houver router.
        
        for slice_usd in plan:
            # Preço com Maker Bias para garantir execução (0.1% desconto na compra)
            execution_price = op.spot_price * 0.999 
            qty = slice_usd / execution_price

            # Criação da Intenção de Ordem
            intent = OrderIntent(
                symbol=op.symbol,
                exchange=op.exchange_spot,
                side="BUY",
                order_type="LIMIT",
                price=execution_price,
                quantity=qty,
                notional_usd=slice_usd
            )

            # 3. Envio físico F7.3 (Se houver router conectado)
            if router:
                order = await router.place_limit(intent)
                if not order: 
                    op.status = "EXECUTION_FAILED"
                    op.exec_abort_reason = "ROUTER_ERROR"
                    break 

            executed_usd += slice_usd

        # Define status final
        if executed_usd >= getattr(op, 'order_recommend_usd', 0) * 0.95:
            op.status = "EXECUTED"
        elif executed_usd > 0:
            op.status = "PARTIAL_FILL"

        return {
            "executed_usd": executed_usd,
            "timestamp": datetime.utcnow()
        }