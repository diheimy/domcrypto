import time
import threading
import statistics
import logging

logger = logging.getLogger("LiquidityState")

class TopLiquidityState:
    """
    F5 - Monitora a estabilidade da liquidez de topo (Top of Book).
    Detecta 'Flickering' e valida se a liquidez é real ou spoofing.
    """
    def __init__(self, max_history=20):
        self._lock = threading.Lock()
        self._state = {} # uid -> history list [values]
        self.max_history = max_history

    def update(self, op):
        uid = getattr(op, 'uid', None)
        if not uid: return op

        val = op.top_liquidity_usd

        with self._lock:
            history = self._state.get(uid, [])
            history.append(val)
            
            if len(history) > self.max_history:
                history.pop(0)
            
            self._state[uid] = history
            
            # Cálculos F5
            if len(history) > 2:
                avg = statistics.mean(history)
                # Desvio Padrão Amostral
                stdev = statistics.stdev(history)
                
                op.top_liquidity_avg = round(avg, 2)
                
                # Volatilidade da Liquidez (%)
                if avg > 0:
                    vol_pct = (stdev / avg) * 100
                else:
                    vol_pct = 0.0
                
                op.top_liquidity_volatility = round(vol_pct, 1)
                
                # Score de Estabilidade (0-100)
                # Menor vol = Maior estabilidade
                # Se vol > 30%, estabilidade tende a zero
                stability = max(0, 100 - (vol_pct * 3.3))
                op.top_liquidity_stability = int(stability)
                
            else:
                op.top_liquidity_avg = val
                op.top_liquidity_volatility = 0.0
                op.top_liquidity_stability = 100 # Assume estável no início

            # Geração de Flags F5 (Tags)
            flags = []
            
            # Tamanho do Livro
            if op.top_liquidity_avg < 50:
                flags.append("THIN_TOP") # Livro fino (< $50)
            elif op.top_liquidity_avg > 250:
                flags.append("SOLID_TOP") # Livro robusto (> $250)
            else:
                flags.append("OK_TOP") # Médio

            # Estabilidade do Livro
            if op.top_liquidity_volatility > 30:
                flags.append("FLICKERING_BOOK") # Liquidez piscando
            elif op.top_liquidity_volatility < 10:
                flags.append("STABLE_BOOK") # Liquidez confiável
            
            # Anexa as flags temporariamente (QualityEngine vai consolidar)
            op.liquidity_flags = flags

        return op

    def cleanup(self):
        # Implementar limpeza se necessário (igual PersistenceState)
        pass