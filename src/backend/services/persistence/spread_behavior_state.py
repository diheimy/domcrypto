import time
import threading
import logging

logger = logging.getLogger("SpreadBehavior")

class SpreadBehaviorState:
    """
    Analisa o comportamento do spread ao longo do tempo (F4.1).
    Detecta fechamento (lucro), inversão (prejuízo) e estabilidade.
    """

    def __init__(self, max_history=50, ttl_seconds=600):
        self._lock = threading.Lock()
        self._state = {}  # Map: uid -> history list
        self.max_history = max_history
        self.ttl = ttl_seconds

    def update(self, op):
        """
        Adiciona snapshot atual e calcula métricas comportamentais.
        """
        uid = getattr(op, 'uid', None)
        if not uid:
            return op # Segurança: se não tiver UID (F4), não faz nada

        now = time.time()

        with self._lock:
            history = self._state.get(uid, [])

            # Snapshot do momento
            current = {
                "ts": now,
                "spread": op.spread_net_pct,
                # 1 = Positivo, -1 = Negativo/Invertido, 0 = Neutro
                "sign": 1 if op.spread_net_pct > 0 else -1 if op.spread_net_pct < 0 else 0
            }

            history.append(current)

            # Limita tamanho do histórico (Janela Deslizante)
            if len(history) > self.max_history:
                history.pop(0)

            self._state[uid] = history

            # === CÁLCULO DE MÉTRICAS (Behavior Analysis) ===
            seen = len(history)
            closed = 0
            inverted = 0
            
            # Analisa transições (t vs t-1)
            for i in range(1, len(history)):
                prev = history[i - 1]
                curr = history[i]

                # Detecção de Fechamento (Sucesso Teórico)
                # Spread era positivo e foi para quase zero (margem de 0.05%)
                if prev["spread"] > 0.1 and abs(curr["spread"]) < 0.05:
                    closed += 1

                # Detecção de Inversão (Armadilha)
                # Spread era positivo e virou negativo
                if prev["sign"] == 1 and curr["sign"] == -1:
                    inverted += 1

            # === ENRIQUECIMENTO DO OP (Output) ===
            op.spread_seen_count = seen
            op.spread_closed_count = closed
            op.spread_inverted_count = inverted

            # Taxa de sucesso (quantas vezes fechou vs quantas vezes foi visto)
            # Nota: É uma métrica aproximada para curto prazo
            if seen > 0:
                op.spread_success_rate = round((closed / seen) * 100, 1)
            else:
                op.spread_success_rate = 0.0

            # Flags Comportamentais (Tags Semânticas)
            flags = []
            
            # TRAP: Inverteu mais de uma vez na janela recente
            if inverted >= 1: 
                flags.append("TRAP")
            
            # UNSTABLE: Nunca fechou e já temos histórico razoável
            if closed == 0 and seen >= 15:
                flags.append("UNSTABLE")
                
            # SOLID: Viu bastante, nunca inverteu
            if seen >= 20 and inverted == 0 and closed > 0:
                flags.append("SOLID")

            op.behavior_flags = flags

        return op

    def cleanup(self):
        """
        Garbage Collector para não estourar memória.
        """
        now = time.time()
        with self._lock:
            expired = [
                uid for uid, h in self._state.items()
                if h and (now - h[-1]["ts"] > self.ttl)
            ]
            for uid in expired:
                del self._state[uid]