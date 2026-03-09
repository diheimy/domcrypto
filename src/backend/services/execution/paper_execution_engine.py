import logging

logger = logging.getLogger("PaperTrading")

class PaperTradingEngine:
    """
    F5.5 - Executa virtualmente o plano do F5.4 (Simulation)
    e calcula PnL realista (Paper Trade).
    """
    @staticmethod
    def execute(op):
        try:
            # Recupera os slices gerados pelo Simulador F5.4
            slices = getattr(op, 'exec_slices', [])
            flags = getattr(op, 'exec_flags', [])
            
            # Se não houve simulação de slices, aborta
            if not slices or "NO_ORDER" in flags or "SIM_ERROR" in flags:
                op.paper_status = "ABORTED"
                return op

            total_usd = 0.0
            total_qty = 0.0
            total_fees = 0.0

            spot_cost = 0.0
            fut_rev = 0.0

            # Taxas Estimadas (0.1% cada ponta = 0.2% total)
            FEE_RATE = 0.002 

            for s in slices:
                usd = s["usd"]
                spot_price = s["spot_price"]
                fut_price = s["fut_price"]

                qty = usd / spot_price

                spot_cost += qty * spot_price
                fut_rev += qty * fut_price

                fee = usd * FEE_RATE
                total_fees += fee

                total_usd += usd
                total_qty += qty

            if total_qty == 0:
                op.paper_status = "ABORTED"
                return op

            # Resultados Financeiros
            gross_pnl = fut_rev - spot_cost
            net_pnl = gross_pnl - total_fees

            pnl_pct = 0.0
            if spot_cost > 0:
                pnl_pct = (net_pnl / spot_cost) * 100

            # Slippage Real vs Spread Inicial
            # (Quanto perdeu do spread teórico até o spread médio executado)
            exec_spread = 0.0
            if op.exec_avg_price_spot > 0:
                exec_spread = ((op.exec_avg_price_fut - op.exec_avg_price_spot) / op.exec_avg_price_spot) * 100
            
            paper_slip = max(0.0, op.spread_pct - exec_spread)

            # Definição de Status
            if "FULL_FILL" in flags:
                status = "FILLED"
            elif "PARTIAL_FILL" in flags:
                status = "PARTIAL"
            else:
                status = "ABORTED"

            # Persistência no Objeto
            op.paper_executed_usd = round(total_usd, 2)
            op.paper_pnl_usd = round(net_pnl, 2)
            op.paper_pnl_pct = round(pnl_pct, 3)
            op.paper_fees_usd = round(total_fees, 2)
            op.paper_slippage_pct = round(paper_slip, 3)
            op.slippage_actual = op.paper_slippage_pct # Alias para UI
            op.paper_status = status

            return op

        except Exception as e:
            logger.error(f"PaperTrading error: {e}")
            # Em caso de erro, garantimos que o campo existe para não quebrar o pipeline
            if not hasattr(op, 'paper_status'):
                op.paper_status = "ERROR"
            return op