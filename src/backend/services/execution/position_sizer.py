from src.backend.models.opportunity import Opportunity

class PositionSizer:
    """
    Define o tamanho da posição (Alocação de Capital).
    Não executa, apenas calcula o valor ideal em USD.
    """

    @staticmethod
    def size(op: Opportunity, base_capital_usd: float) -> float:
        """
        Calcula o tamanho da ordem baseado na qualidade (Score) da oportunidade.
        Escala linear conservadora.
        """
        # Proteção contra inputs inválidos
        if base_capital_usd <= 0:
            return 0.0

        # Tier S: Oportunidade Excelente (Score 90+) -> 5% da banca
        if op.score >= 90:
            return base_capital_usd * 0.05
            
        # Tier A: Oportunidade Muito Boa (Score 80+) -> 3% da banca
        if op.score >= 80:
            return base_capital_usd * 0.03
            
        # Tier B: Oportunidade Boa (Score 70+) -> 2% da banca
        if op.score >= 70:
            return base_capital_usd * 0.02
            
        # Tier C: Oportunidade Média (Score 60+) -> 1% da banca
        # Abaixo de 60 o RiskGate já deve ter bloqueado, mas por segurança retornamos o mínimo
        return base_capital_usd * 0.01