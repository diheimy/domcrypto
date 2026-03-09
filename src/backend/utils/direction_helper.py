from typing import List

def extract_direction(tags: List[str]) -> str:
    """
    Extrai a direção predominante da arbitragem baseada nas tags.
    Centraliza o vocabulário de direção do sistema.
    """
    if not tags:
        return "unknown"
    
    # Ordem de prioridade (se houver conflito, o primeiro vence)
    if "spot_to_futures" in tags:
        return "spot_to_futures"
    
    if "futures_to_spot" in tags:
        return "futures_to_spot"
        
    return "unknown"