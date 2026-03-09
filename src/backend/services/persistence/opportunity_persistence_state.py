import time
import threading
import logging
import statistics

logger = logging.getLogger("Persistence")

class OpportunityPersistenceState:
    """
    Mantém estado temporal das oportunidades (Memória Volátil).
    Responsável por calcular persistência e estabilidade.
    """

    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self._lock = threading.Lock()
        self._state = {}  # Map: uid -> {first_seen, last_seen, history, ...}

    def update(self, op):
        """
        Atualiza o histórico da oportunidade e enriquece o objeto 'op'
        com dados temporais (persistence_minutes, volatility_pct).
        """
        now = time.time()
        
        # 1. Identidade Única (Canonical Key)
        # Ex: BTC/USDT:mexc:gate_futures
        uid = f"{op.symbol}:{op.exchange_spot}:{op.exchange_futures}"
        op.uid = uid

        with self._lock:
            record = self._state.get(uid)

            if not record:
                # Primeira vez que vemos
                record = {
                    "first_seen": now,
                    "last_seen": now,
                    "samples": 1,
                    "spread_history": [op.spread_net_pct],
                }
                self._state[uid] = record
                
                # Valores iniciais para o objeto
                op.persistence_minutes = 0
                op.volatility_pct = 0.0
                
            else:
                # Atualização (Reencontro)
                record["last_seen"] = now
                record["samples"] += 1
                record["spread_history"].append(op.spread_net_pct)

                # Janela deslizante de histórico (últimas 20 amostras)
                if len(record["spread_history"]) > 20:
                    record["spread_history"].pop(0)

                # 2. Enriquecimento (Cálculo Temporal)
                # Persistência em minutos
                seconds_alive = now - record["first_seen"]
                op.persistence_minutes = int(seconds_alive / 60)

                # Volatilidade / Estabilidade
                op.volatility_pct = self._calc_volatility(record["spread_history"])

        return op

    def _calc_volatility(self, spreads):
        """
        Calcula o Desvio Padrão do spread histórico.
        Quanto maior, mais instável (pior).
        """
        if len(spreads) < 2:
            return 0.0
        
        try:
            # Desvio padrão da amostra
            return round(statistics.stdev(spreads), 2)
        except:
            return 0.0

    def cleanup(self):
        """
        Garbage Collector: Remove oportunidades que sumiram há mais de TTL segundos.
        """
        now = time.time()
        with self._lock:
            # Identifica UIDs mortos
            expired_uids = [
                uid for uid, rec in self._state.items() 
                if (now - rec["last_seen"]) > self.ttl
            ]
            
            # Remove
            for uid in expired_uids:
                del self._state[uid]
            
            if expired_uids:
                logger.info(f"Cleanup: Removidos {len(expired_uids)} itens expirados.")