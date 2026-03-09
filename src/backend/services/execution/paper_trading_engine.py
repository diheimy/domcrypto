import logging

logger = logging.getLogger("PaperTrading")

class PaperTradingEngine:
    """
    F5.5 - Executa virtualmente o plano do F5.4 e calcula PnL realista.
    Transforma 'intenção de execução' em 'resultado contábil'.
    """
    
    @staticmethod
    def execute(op):
        try:
            slices = getattr(op, 'exec_slices', [])
            flags = getattr(op, 'exec_flags', [])
            
            # Se não houve slices ou a ordem foi abortada antes de começar
            if not slices or "NO_ORDER" in flags or "NO_BOOK_DATA" in flags:
                op.paper_status = "ABORTED"
                return op

            total_usd = 0.0
            total_qty = 0.0
            total_fees = 0.0

            spot_cost = 0.0
            fut_rev = 0.0

            # Taxa Total: 0.1% Spot + 0.1% Futuros = 0.2%
            # Multiplicador: 0.002
            FEE_RATE = 0.002 

            for s in slices:
                usd = float(s.get("usd", 0))
                spot_price = float(s.get("spot_price", 0))
                fut_price = float(s.get("fut_price", 0))
                
                if spot_price <= 0: continue

                qty = usd / spot_price

                # Custo da perna Spot (Compra)
                spot_cost += qty * spot_price
                
                # Receita da perna Futuros (Venda)
                fut_rev += qty * fut_price

                # Taxas sobre o volume notional
                fee = usd * FEE_RATE
                total_fees += fee

                total_usd += usd
                total_qty += qty

            if total_qty == 0:
                op.paper_status = "ABORTED"
                return op

            # PnL Bruto (Diferença de preços)
            gross_pnl = fut_rev - spot_cost
            
            # PnL Líquido (Descontando taxas)
            net_pnl = gross_pnl - total_fees

            # ROE % (Retorno sobre o capital investido no Spot)
            pnl_pct = 0.0
            if spot_cost > 0:
                pnl_pct = (net_pnl / spot_cost) * 100

            # Slippage Realizado: Diferença entre o Spread Líquido TEÓRICO e o Spread FINAL da execução
            # spread_net_pct (Teórico Topo) - exec_final_spread (Realizado Médio - Taxas Embutidas na simulação)
            # Mas cuidado: exec_final_spread no simulador é bruto. Vamos recalcular aqui.
            
            avg_spot = spot_cost / total_qty
            avg_fut = fut_rev / total_qty
            spread_realized_gross = ((avg_fut - avg_spot) / avg_spot) * 100
            spread_realized_net = spread_realized_gross - (FEE_RATE * 100)
            
            paper_slip = max(0.0, op.spread_net_pct - spread_realized_net)

            # Definição de Status
            if "FULL_FILL" in flags:
                status = "EXECUTED"
            elif "PARTIAL_FILL" in flags:
                status = "PARTIAL"
            elif "SLIPPAGE_LIMIT" in flags:
                status = "PARTIAL_SLIPPAGE"
            else:
                status = "ABORTED"
            
            # Se deu prejuízo no paper trade, marca flag visual
            if net_pnl < 0:
                status = "LOSS"

            # Persistência no objeto
            op.paper_executed_usd = round(total_usd, 2)
            op.paper_pnl_usd = round(net_pnl, 2)
            op.paper_pnl_pct = round(pnl_pct, 3)
            op.paper_fees_usd = round(total_fees, 2)
            op.paper_slippage_pct = round(paper_slip, 3)
            op.paper_status = status

            return op

        except Exception as e:
            logger.error(f"PaperTrading error: {e}")
            op.paper_status = "ERROR"
            return op