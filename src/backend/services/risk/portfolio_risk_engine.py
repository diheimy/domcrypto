class PortfolioRiskEngine:
    @staticmethod
    def approve(op, portfolio):
        reasons = []
        rec_usd = getattr(op, 'order_recommend_usd', 0)
        future_total = portfolio.total_exposure_usd + rec_usd

        # REGRA: Concentração Dinâmica por Exchange
        exch_limit = min(
            portfolio.total_capital * 0.40,
            future_total * 0.60 if future_total > 0 else portfolio.total_capital
        )
        
        future_exch_exposure = portfolio.exchange_exposure[op.exchange_spot] + rec_usd
        if future_exch_exposure > exch_limit:
            reasons.append(f"EXCHANGE_CONCENTRATION_LIMIT:{op.exchange_spot}")

        # Verificação de Drawdown Diário
        if portfolio.daily_pnl <= (portfolio.total_capital * -0.02):
            reasons.append("DAILY_DRAWDOWN_LIMIT")
        
        if reasons:
            op.risk_decision = "BLOCKED"
            op.risk_reasons = reasons
            return False

        op.risk_decision = "APPROVED"
        return True