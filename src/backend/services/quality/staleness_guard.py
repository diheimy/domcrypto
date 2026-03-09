import time

class StalenessGuard:
    """
    F7.1 — Staleness Guard
    Bloqueia oportunidades com dados de book atrasados (Stale Data).
    Evita 'Latency Arbitrage' acidental (ver lucro onde o preço já mudou).
    """

    # Janela de tolerância: 1.5 segundos (1500ms)
    # Acima disso, o dado é considerado 'velho' para HFT/Arbitragem.
    MAX_AGE_MS = 6000 

    @staticmethod
    def is_fresh(ticker: dict, now_ms: float) -> bool:
        """
        Retorna True se o ticker estiver dentro da janela aceitável.
        Retorna False se for velho ou não tiver timestamp.
        """
        ts = ticker.get("timestamp")
        
        # Se não tem timestamp, não é confiável. Rejeita.
        if not ts:
            return False 

        # Calcula idade do dado
        age = now_ms - ts
        
        # Aceita apenas se for mais novo que o limite
        return age <= StalenessGuard.MAX_AGE_MS