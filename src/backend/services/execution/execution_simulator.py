import logging
import copy

logger = logging.getLogger("ExecutionSimulator")

class ExecutionSimulator:
    """
    F5.4 (Advanced) - Simula execução com Participation Rate Dinâmico
    e métricas de eficiência.
    """
    
    @staticmethod
    def simulate(op, max_slippage_pct=0.5):
        try:
            order_usd = getattr(op, 'order_recommend_usd', 0)
            risk_level = getattr(op, 'order_risk_level', 'HIGH')
            
            # Reset de campos
            op.exec_abort_reason = ""
            op.exec_efficiency = 0.0
            
            if order_usd <= 0:
                op.exec_flags.append("NO_ORDER")
                op.exec_abort_reason = "ZERO_RECOMMENDATION"
                return op

            spot_book_raw = getattr(op, '_temp_spot_book', [])
            fut_book_raw = getattr(op, '_temp_fut_book', [])
            
            if not spot_book_raw or not fut_book_raw:
                op.exec_flags.append("NO_BOOK_DATA")
                op.exec_abort_reason = "MISSING_BOOKS"
                return op

            # [AJUSTE 1] Participation Rate Dinâmico
            # Define agressividade baseada no risco estrutural (F5.3)
            participation_rate = 0.20 # Padrão conservador (HIGH)
            
            if risk_level == 'SAFE':
                participation_rate = 0.35 # Agressivo em book forte
            elif risk_level == 'MODERATE':
                participation_rate = 0.25 # Balanceado
            
            # Deep Copy para simulação
            spot_book = copy.deepcopy(spot_book_raw)
            fut_book = copy.deepcopy(fut_book_raw)

            remaining_usd = order_usd
            slices = []

            cum_spot_cost = 0.0
            cum_fut_rev = 0.0
            cum_qty = 0.0

            idx_s = 0
            idx_f = 0
            
            base_spread = op.spread_net_pct

            # --- LOOP DE EXECUÇÃO ---
            while remaining_usd > 10 and idx_s < len(spot_book) and idx_f < len(fut_book):
                s_price, s_qty = spot_book[idx_s]
                f_price, f_qty = fut_book[idx_f]

                # Aplica o Participation Rate dinâmico
                max_qty_level = min(s_qty, f_qty) * participation_rate
                max_usd_level = max_qty_level * s_price

                slice_usd = min(max_usd_level, remaining_usd)
                
                if slice_usd < 10:
                    if s_qty < f_qty: idx_s += 1
                    else: idx_f += 1
                    continue

                slice_qty = slice_usd / s_price

                # --- SIMULAÇÃO DE IMPACTO ---
                temp_spot_cost = cum_spot_cost + (slice_qty * s_price)
                temp_fut_rev = cum_fut_rev + (slice_qty * f_price)
                temp_qty = cum_qty + slice_qty
                
                avg_spot = temp_spot_cost / temp_qty
                avg_fut = temp_fut_rev / temp_qty
                
                spread_now_bruto = ((avg_fut - avg_spot) / avg_spot) * 100
                spread_now_liq = spread_now_bruto - 0.2
                
                slippage_actual = base_spread - spread_now_liq

                # [AJUSTE 2] Motivo do Abort
                # Stop Loss de Slippage
                if slippage_actual > max_slippage_pct:
                    op.exec_flags.append("SLIPPAGE_LIMIT")
                    op.exec_abort_reason = f"SLIPPAGE > {max_slippage_pct}%"
                    break
                    
                # Stop Loss de Lucro (Spread virou pó)
                if spread_now_liq <= 0.05:
                    op.exec_flags.append("PROFIT_LIMIT")
                    op.exec_abort_reason = "SPREAD < 0.05%"
                    break

                # Confirma Slice
                slices.append({
                    "usd": round(slice_usd, 2),
                    "spot_price": round(s_price, 6),
                    "fut_price": round(f_price, 6),
                    "spread_marginal": round(spread_now_liq, 2)
                })

                cum_spot_cost += slice_qty * s_price
                cum_fut_rev += slice_qty * f_price
                cum_qty += slice_qty

                remaining_usd -= slice_usd

                # Consome book
                spot_book[idx_s][1] -= slice_qty
                fut_book[idx_f][1] -= slice_qty
                
                # Consumo tático do restante do nível (simula competição)
                competitor_burn = 1.0 / participation_rate # Inverso da taxa
                spot_book[idx_s][1] -= (slice_qty * (competitor_burn - 1))
                fut_book[idx_f][1] -= (slice_qty * (competitor_burn - 1))

                if spot_book[idx_s][1] <= 1e-9: idx_s += 1
                if fut_book[idx_f][1] <= 1e-9: idx_f += 1

            # --- RESULTADOS FINAIS ---
            if cum_qty > 0:
                op.exec_total_usd = round(order_usd - remaining_usd, 2)
                op.exec_avg_price_spot = cum_spot_cost / cum_qty
                op.exec_avg_price_fut = cum_fut_rev / cum_qty
                op.exec_final_spread = ((op.exec_avg_price_fut - op.exec_avg_price_spot)
                                        / op.exec_avg_price_spot) * 100
            
            # [AJUSTE 3] Métrica de Eficiência Institucional
            if order_usd > 0:
                op.exec_efficiency = round(op.exec_total_usd / order_usd, 2)

            # Flags Finais
            if remaining_usd <= 10 and not op.exec_abort_reason:
                op.exec_flags.append("FULL_FILL")
                op.exec_abort_reason = "COMPLETED"
            elif remaining_usd > 10 and not op.exec_abort_reason:
                op.exec_flags.append("PARTIAL_FILL")
                op.exec_abort_reason = "BOOK_EXHAUSTED" # Acabou a liquidez disponível nos parâmetros

            op.exec_slices = slices
            return op

        except Exception as e:
            logger.error(f"Erro ExecutionSimulator: {e}")
            op.exec_flags.append("SIM_ERROR")
            op.exec_abort_reason = "EXCEPTION"
            return op