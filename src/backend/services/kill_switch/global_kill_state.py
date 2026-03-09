import threading
from datetime import datetime

class GlobalKillState:
    """
    Estado do Kill Switch Global (Thread-Safe).
    Suporta estados progressivos: NORMAL -> DEGRADED -> KILL.
    """
    # Estados
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    KILL = "KILL"

    def __init__(self):
        self._state = self.NORMAL
        self._reason = None
        self._timestamp = None
        self._consecutive_errors = 0
        self._lock = threading.Lock()

    @property
    def state(self):
        with self._lock:
            return self._state

    @property
    def reason(self):
        with self._lock:
            return self._reason

    def is_active(self):
        """Retorna True se o sistema estiver em estado KILL."""
        with self._lock:
            return self._state == self.KILL

    def is_degraded(self):
        """Retorna True se o sistema estiver em estado DEGRADED."""
        with self._lock:
            return self._state == self.DEGRADED

    def register_error(self, reason: str):
        """
        Incrementa contador de erros e escala o estado.
        1 erro -> DEGRADED
        >= 3 erros -> KILL
        """
        with self._lock:
            self._consecutive_errors += 1
            self._reason = reason
            self._timestamp = datetime.utcnow()
            
            if self._consecutive_errors >= 3:
                self._state = self.KILL
            else:
                self._state = self.DEGRADED

    def reset(self):
        """Reseta estado para NORMAL."""
        with self._lock:
            self._state = self.NORMAL
            self._reason = None
            self._timestamp = None
            self._consecutive_errors = 0