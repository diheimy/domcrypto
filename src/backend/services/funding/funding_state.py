import time
import threading

class FundingState:
    """
    Estado institucional de funding (cache com TTL).
    Thread-safe para leitura/escrita simultânea.
    """
    def __init__(self, ttl_seconds=300): # 5 min TTL
        self.ttl = ttl_seconds
        self._lock = threading.Lock()
        self._data = {}  # key: (exchange, symbol) -> {rate, ts}

    def get(self, exchange: str, symbol: str):
        key = (exchange, symbol)
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            
            # Validação de TTL
            if time.time() - item["ts"] > self.ttl:
                del self._data[key]
                return None
            
            return item["rate"]

    def set(self, exchange: str, symbol: str, rate_pct: float):
        key = (exchange, symbol)
        with self._lock:
            self._data[key] = {
                "rate": rate_pct,
                "ts": time.time()
            }