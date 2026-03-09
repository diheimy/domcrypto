from .base_exit_model import ExitModel

class TimeExit(ExitModel):
    """
    Fecha se o trade durar mais que o tempo maximo permitido.
    """

    def __init__(self, max_holding_seconds: int = 6 * 3600):
        self.max_seconds = max_holding_seconds

    def evaluate(self, snapshot, now, *args):
        elapsed = (now - snapshot.timestamp).total_seconds()

        if elapsed >= self.max_seconds:
            return True, f"TIME_EXIT_{int(elapsed)}s"

        return False, "HOLD_TIME_OK"
