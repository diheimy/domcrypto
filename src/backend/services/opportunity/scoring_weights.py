from dataclasses import dataclass

@dataclass(frozen=True)
class ScoringWeights:
    spread: float
    liquidity: float
    health: float
    direction: float

# Mapa de pesos por perfil
# A soma ideal dos pesos é 1.0 (para manter escala), mas não é obrigatório.
SCORING_WEIGHTS = {
    "conservative": ScoringWeights(
        spread=0.25,    # Spread importa menos que segurança
        liquidity=0.40, # Liquidez é rei
        health=0.30,    # Saúde estrutural é vital
        direction=0.05
    ),
    "balanced": ScoringWeights(
        spread=0.45,    # Equilíbrio clássico
        liquidity=0.30,
        health=0.20,
        direction=0.05
    ),
    "aggressive": ScoringWeights(
        spread=0.65,    # Foco total no lucro bruto
        liquidity=0.20, # Aceita books mais finos
        health=0.10,    # Aceita maior risco estrutural
        direction=0.05
    ),
}