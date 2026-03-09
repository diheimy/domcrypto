# CORREÇÃO: Importar direto de app.config (sem .constants)
from src.backend.config import (
    BACKEND_MIN_VOLUME_USD,
    BACKEND_MIN_SPREAD_PCT
)

def enforce(opportunity) -> bool:
    if opportunity.volume_24h < BACKEND_MIN_VOLUME_USD:
        return False

    if opportunity.spread_pct < BACKEND_MIN_SPREAD_PCT:
        return False

    return True