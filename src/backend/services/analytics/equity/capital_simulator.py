class CapitalSimulator:
    """
    Simulador de evolução de capital.
    Útil para projeções futuras baseadas em estatísticas passadas.
    """
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital

    def simulate_compound(self, pnl_percentages: list) -> float:
        """
        Simula o capital final assumindo reinvestimento total dos lucros.
        pnl_percentages: Lista de % de retorno por trade (ex: 0.5, -0.2, 1.2)
        """
        capital = self.initial_capital
        for pct in pnl_percentages:
            capital = capital * (1 + (pct / 100))
        return round(capital, 2)