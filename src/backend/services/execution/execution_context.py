from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionContext:
    """
    Estado global de prontidão para execução.
    Captura o 'clima' macro do sistema (Risco Sistêmico).
    Imutável por ciclo.
    """

    # Métricas vindas do RiskMetrics (Etapa 6)
    diversification_index: float      # 0.0 a 1.0 (Quanto maior, pior)
    high_score_dependency: float      # 0.0 a 1.0 (Dependência de balas de prata)
    
    # Limites de Tolerância (Policy)
    max_allowed_concentration: float = 0.35  # Se HHI > 0.35, sistema está muito concentrado
    max_high_score_dependency: float = 0.70  # Se > 70% depende de score alto, sistema está frágil

    @property
    def is_healthy(self) -> bool:
        """
        Kill Switch Sistêmico.
        Se retornar False, nenhuma ordem deve ser emitida, independente da qualidade da oportunidade.
        """
        return (
            self.diversification_index <= self.max_allowed_concentration
            and self.high_score_dependency <= self.max_high_score_dependency
        )