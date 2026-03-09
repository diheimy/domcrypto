import time
import threading
from collections import deque

class TrustState:
    """
    F12 — Estado institucional de confiança.
    Armazena histórico de execuções reais chaveado por (exchange, symbol, hour).
    Possui Normalização de chaves para evitar duplicação (ex: mexc_futures -> mexc).
    """

    def __init__(self, max_history=50, ttl_seconds=3600):
        self.max_history = max_history
        self.ttl = ttl_seconds
        self._lock = threading.Lock()
        self._data = {}  # key -> {executions: deque, ts: float}

    def _bucket_hour(self):
        # Retorna o timestamp da hora atual (para agrupar dados por hora)
        return int(time.time() // 3600)

    def _norm_exch(self, exchange):
        # [BLINDAGEM] Normalização crítica de exchange
        # Garante que 'mexc', 'mexc_futures' e 'MEXC' caiam na mesma chave
        if not exchange:
            return "unknown"
        return exchange.lower().replace("_futures", "").replace("_spot", "")

    def update(self, exchange, symbol, exec_data: dict):
        # Normaliza exchange
        clean_exch = self._norm_exch(exchange)
        
        # Chave composta: Exchange + Símbolo + Hora Atual
        key = (clean_exch, symbol, self._bucket_hour())

        with self._lock:
            item = self._data.get(key)
            if not item:
                item = {
                    "executions": deque(maxlen=self.max_history),
                    "ts": time.time()
                }
                self._data[key] = item

            item["executions"].append(exec_data)
            item["ts"] = time.time()

    def get(self, exchange, symbol):
        # Normaliza exchange
        clean_exch = self._norm_exch(exchange)
        
        scores = []

        with self._lock:
            # Itera sobre cópia dos itens para poder deletar expirados
            for (ex, sym, bucket), item in list(self._data.items()):
                # Limpeza de memória (TTL Check)
                if time.time() - item["ts"] > self.ttl:
                    del self._data[(ex, sym, bucket)]
                    continue

                # Compara com a chave normalizada
                if ex == clean_exch and sym == symbol:
                    scores.extend(item["executions"])

        return scores