import asyncio
import logging
from collections import Counter
from src.backend.services.fetch.fetch_service import FetchService
from src.backend.pipeline.opportunity_builder import OpportunityBuilder
from src.backend.services.quality.quality_engine import QualityEngine
from src.backend.services.persistence.opportunity_persistence_state import OpportunityPersistenceState
from src.backend.services.persistence.spread_behavior_state import SpreadBehaviorState
from src.backend.services.market_data.top_liquidity_state import TopLiquidityState
from src.backend.services.fees.fee_engine import FeeEngine
from src.backend.services.funding.funding_engine import FundingEngine
from src.backend.services.capital.capital_allocation_engine import CapitalAllocationEngine
from src.backend.services.execution.smart_execution_engine import SmartExecutionEngine
from src.backend.services.execution.slippage_quality_engine import SlippageQualityEngine
from src.backend.services.trust.trust_state import TrustState
from src.backend.services.trust.trust_engine import TrustEngine
from src.backend.services.quality.adaptive_scoring_engine import AdaptiveScoringEngine
from src.backend.services.market_regime.market_regime_engine import MarketRegimeEngine
from src.backend.services.exit.exit_engine import ExitEngine
from src.backend.services.rebalance.partial_rebalance_engine import PartialRebalanceEngine
from src.backend.services.kill_switch.global_kill_state import GlobalKillState
from src.backend.services.kill_switch.global_kill_engine import GlobalKillEngine
from src.backend.services.risk.portfolio_risk_engine import PortfolioRiskEngine
from src.backend.services.risk.portfolio_state import PortfolioRiskState
from src.backend.services.execution.execution_engine import ExecutionEngine
from src.backend.services.risk.portfolio_updater import PortfolioUpdater

# Hard rules (AUTO): a UI (manual) deve receber o feed completo.
# A execução automática usa este piso para decidir elegibilidade.
from src.backend.config import BACKEND_MIN_VOLUME_USD, BACKEND_MIN_SPREAD_PCT

try:
    from src.backend.services.notification.notification_service import NotificationService
    HAS_NOTIFICATIONS = True
except ImportError:
    HAS_NOTIFICATIONS = False

logger = logging.getLogger("Pipeline")

class OpportunityPipeline:
    def __init__(self, risk_state: PortfolioRiskState, execution_engine: ExecutionEngine):
        self.fetch_service = FetchService()
        self.risk_state = risk_state
        self.execution_engine = execution_engine
        self.persistence_state = OpportunityPersistenceState(ttl_seconds=300)
        self.behavior_state = SpreadBehaviorState(max_history=50, ttl_seconds=600)
        self.liquidity_state = TopLiquidityState()
        self.trust_state = TrustState()
        self.global_kill_state = GlobalKillState()
        
        if self.global_kill_state.is_active():
            logger.critical(f"🔥 ALERTA: Global Kill Switch iniciou ATIVO! Motivo: {self.global_kill_state.reason}")

    @staticmethod
    def _compute_auto_gate(op):
        """Define campos para execução automática.

        Regra de ouro: o backend envia o FEED COMPLETO ao frontend.
        Este gate serve apenas para o fluxo automático (paper/real).
        """
        reasons = []

        # Piso institucional (auto)
        if getattr(op, 'volume_24h_usd', 0.0) < BACKEND_MIN_VOLUME_USD:
            reasons.append(f"MIN_VOL<{BACKEND_MIN_VOLUME_USD:,.0f}")

        # Spread mínimo (auto) - usamos spread líquido (após fees)
        if getattr(op, 'spread_net_pct', 0.0) < BACKEND_MIN_SPREAD_PCT:
            reasons.append(f"MIN_SPREAD<{BACKEND_MIN_SPREAD_PCT:.2f}")

        status = (getattr(op, 'status', '') or '').upper()
        if 'KILLED' in status:
            reasons.append("KILLED")
        if status == 'OBSERVATION_ONLY':
            reasons.append("OBSERVATION")

        risk_level = (getattr(op, 'order_risk_level', '') or '').upper()
        if risk_level == 'BLOCKED':
            reasons.append("RISK_BLOCKED")

        # Persistimos flags no modelo (não quebra versões antigas)
        try:
            op.auto_block_reasons = reasons
            op.auto_eligible = (len(reasons) == 0)
        except Exception:
            pass

        return op

    async def run(self):
        try:
            # 🔧 SOFT RESET MONITORADO
            if self.global_kill_state.is_active():
                logger.warning("♻️ Kill Switch: Reiniciando ciclo para reavaliação de mercado...")
                self.global_kill_state.reset()
            
            spot_data, futures_data = await self.fetch_service.fetch_all()
            
            total_spot = sum(len(x) for x in spot_data.values())
            total_fut = sum(len(x) for x in futures_data.values())
            
            if total_spot == 0 and total_fut == 0:
                logger.warning(f"⚠️ FETCH TOTAL ZERO. Verifique conexão.")
                return []

            raw_opportunities = OpportunityBuilder.build_batch(spot_data, futures_data)
            count_raw = len(raw_opportunities)
            processed_opportunities = []

            for op in raw_opportunities:
                try:
                    # --- A. Enriquecimento ---
                    op = self.persistence_state.update(op)
                    op = self.liquidity_state.update(op)
                    op = self.behavior_state.update(op)
                    op = QualityEngine.enrich(op)

                    if op.exchange_futures and op.symbol:
                        execs = self.trust_state.get(op.exchange_futures, op.symbol)
                        trust_score = TrustEngine.compute(op.exchange_futures, op.symbol, execs)
                        op = AdaptiveScoringEngine.apply(op, trust_score)

                    op = MarketRegimeEngine.detect(op)
                    if op.market_regime_factors:
                        op.score_regime_adjusted = int(op.score * op.market_regime_factors.get("score_factor", 1.0))
                    else:
                        op.score_regime_adjusted = op.score

                    op.slippage_actual = getattr(op, 'paper_slippage_pct', 0.0)
                    op.exec_efficiency = getattr(op, 'exec_efficiency', 0.0)
                    op.exec_abort_reason = getattr(op, 'exec_abort_reason', 'N/A')

                    op = FeeEngine.apply(op)
                    if op.exchange_futures and op.symbol:
                        exch_clean = op.exchange_futures.replace("_futures", "").lower()
                        real_funding_rate = await self.fetch_service.funding_fetcher.fetch(exch_clean, op.symbol)
                        if real_funding_rate is not None:
                            op.funding_rate_pct = real_funding_rate
                            # ================================
                            # V113 - Funding em formato decimal
                            # ================================
                            op.funding_rate = real_funding_rate / 100.0
                    op = FundingEngine.apply(op)

                    # ================================
                    # V113 - Atualizar range com min/max spread vistos
                    # ================================
                    if hasattr(op, 'min_spread_seen') and hasattr(op, 'max_spread_seen'):
                        if op.min_spread_seen > 0 and op.max_spread_seen > 0:
                            op.range_low = op.min_spread_seen
                            op.range_high = op.max_spread_seen
                            op.range_pct = max(0.0, op.range_high - op.range_low)

                    # --- B. Governança e Decisão ---
                    
                    # 🔴 F16 Kill Switch (Progressivo)
                    # Se retornar True, significa que o sistema está em KILL ou DEGRADED para este ativo
                    is_killed = GlobalKillEngine.evaluate(op, self.risk_state, self.global_kill_state)
                    
                    if is_killed:
                        # [FIX] Não descarta! Marca e passa para o final.
                        op.mark_killed(reason=self.global_kill_state.reason or "GLOBAL_KILL_UNKNOWN")
                        op = self._compute_auto_gate(op)
                        processed_opportunities.append(op)
                        continue 

                    # F6 Risco - Aprovação
                    approved = PortfolioRiskEngine.approve(op, self.risk_state)
                    
                    if approved:
                        op = CapitalAllocationEngine.apply(op, self.risk_state)
                        op = SmartExecutionEngine.decide(op)

                        # Execução automática: o feed vai para a UI independente,
                        # mas o executor só atua quando a oportunidade é elegível.
                        op = self._compute_auto_gate(op)

                        if op.auto_eligible and op.order_recommend_usd > 0 and op.status != "OBSERVATION_ONLY":
                            result = await self.execution_engine.execute(op)
                            if result:
                                PortfolioUpdater.apply_execution(result, op, self.risk_state)
                                op = SlippageQualityEngine.apply(op, result)
                                op.current_position_usd = op.filled_usd
                                GlobalKillEngine.evaluate(op, self.risk_state, self.global_kill_state)
                                self.trust_state.update(op.exchange_futures, op.symbol, {
                                    "execution_quality_score": op.execution_quality_score,
                                    "fill_ratio": op.fill_ratio,
                                    "slippage_pct": op.slippage_pct,
                                    "execution_status": op.execution_status
                                })

                        if getattr(op, "paper_status", "") == "EXECUTED":
                            op.current_position_usd = max(getattr(op, "current_position_usd", 0.0), getattr(op, "paper_executed_usd", 0.0))
                            op.pnl_pct = getattr(op, "paper_pnl_pct", 0.0)
                            op.holding_hours = max(getattr(op, "holding_hours", 0), 1.0)

                        op = PartialRebalanceEngine.evaluate(op)
                        
                        if HAS_NOTIFICATIONS and op.partial_rebalance_plan and op.filled_usd > 0:
                            await NotificationService.send("⚖️ REBALANCE", f"{op.symbol}", level="INFO")
                        
                        if self.global_kill_state.is_active():
                            op.exit_plan = {"action": "KILL", "urgency": "IMMEDIATE", "reason": ["GLOBAL_KILL_SWITCH"]}
                        else:
                            op = ExitEngine.decide(op)

                        op = self._compute_auto_gate(op)
                        
                        processed_opportunities.append(op)
                    else:
                        op.status = "OBSERVATION_ONLY"
                        if not op.allocation_reason: op.allocation_reason = "RISK_FILTER"
                        op = self._compute_auto_gate(op)
                        processed_opportunities.append(op)
                
                except Exception as e:
                    logger.error(f"❌ Erro op {op.symbol}: {e}")
                    # Em caso de erro de processamento, tenta salvar como ERRO para visibilidade
                    try:
                        op.mark_killed(reason=f"PIPELINE_ERROR: {str(e)}")
                        processed_opportunities.append(op)
                    except:
                        continue

            self.persistence_state.cleanup()
            self.behavior_state.cleanup()
            self.liquidity_state.cleanup()
            
            # Relatório Institucional Detalhado
            status_counts = Counter(op.status for op in processed_opportunities)
            active_count = status_counts.get("ACTIVE", 0) + status_counts.get("READY", 0)
            obs_count = status_counts.get("OBSERVATION_ONLY", 0)
            killed_count = status_counts.get("KILLED", 0)
            
            logger.info(
                f"📊 PIPELINE REPORT: Raw={count_raw} | "
                f"Active={active_count} | Obs={obs_count} | Killed={killed_count}"
            )
            
            return processed_opportunities

        except Exception as e:
            logger.exception("Erro crítico no pipeline")
            return []