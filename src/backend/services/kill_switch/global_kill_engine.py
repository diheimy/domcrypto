import logging
from src.backend.services.risk.portfolio_state import PortfolioRiskState
from src.backend.services.kill_switch.global_kill_state import GlobalKillState
from src.backend.config.settings import SYSTEM_MODE 

logger = logging.getLogger("GlobalKill")

class GlobalKillEngine:
    """
    F16 — Global Kill Switch Engine (Progressivo)
    Monitora a saúde sistêmica.
    NORMAL -> DEGRADED (Aviso/Paper) -> KILL (Travamento)
    """
    
    # Thresholds
    MIN_GLOBAL_LIQUIDITY_USD = 1000.0 
    
    @staticmethod
    def evaluate(op, risk_state: PortfolioRiskState, kill_state: GlobalKillState) -> bool:
        """
        Avalia a saúde do sistema.
        Retorna True APENAS se o sistema estiver em estado KILL (Travado).
        """
        # 1. Se já estiver morto, mantém morto
        if kill_state.is_active():
            return True

        reasons = []

        # --- CHECK 1: Colapso de Liquidez ---
        liq = getattr(op, "top_liquidity_usd", 0.0)
        
        # Só avalia se o dado for válido (>0) para evitar falsos positivos de fetch
        if liq > 0 and liq < GlobalKillEngine.MIN_GLOBAL_LIQUIDITY_USD:
            msg = f"Liquidez Crítica: ${liq:.2f} < ${GlobalKillEngine.MIN_GLOBAL_LIQUIDITY_USD}"
            reasons.append(msg)

        # --- CHECK 2: Regime de Mercado ---
        if getattr(op, "market_regime", "") == "STRESSED":
             reasons.append("Mercado STRESSED")

        # --- DECISÃO ---
        if reasons:
            reason_str = " | ".join(reasons)
            
            # Registra o erro progressivamente (Normal -> Degraded -> Kill)
            kill_state.register_error(reason_str)

            # Verifica novo estado
            if kill_state.is_active():
                # ESTADO KILL (>= 3 erros)
                if SYSTEM_MODE == "SHADOW":
                    logger.warning(f"🛡️ [SHADOW] Kill Switch Disparado (Ignorado): {reason_str}")
                    return False
                else:
                    logger.critical(f"🔥 GLOBAL KILL ATIVADO: {reason_str}")
                    return True
            
            elif kill_state.is_degraded():
                # ESTADO DEGRADED (1-2 erros)
                # Permite processar, mas marca como arriscado
                logger.warning(f"⚠️ Sistema DEGRADED: {reason_str}")
                
                # Garante que tags seja uma lista antes de adicionar
                if not hasattr(op, 'tags') or not isinstance(op.tags, list):
                    op.tags = []
                op.tags.append("SYSTEM_DEGRADED")
                
                # Força modo observação para esta oportunidade
                op.status = "OBSERVATION_ONLY"
                op.execution_decision = "HOLD"
                
                # Retorna False para NÃO matar o pipeline (apenas degradar)
                return False

        return False