class PortfolioUpdater:
    """
    F7.5 - Sincronizador de Exposição Real.
    Atualiza o estado global após o preenchimento da ordem.
    """
    @staticmethod
    def apply_execution(result, op, portfolio):
        executed = result["executed_usd"]

        # Atualiza exposição viva
        portfolio.total_exposure_usd += executed
        portfolio.exchange_exposure[op.exchange_spot] += executed
        portfolio.asset_exposure[op.symbol] += executed

        # Marca como oportunidade em aberto no mercado
        op.status = "OPEN"