from datetime import datetime
from src.backend.services.persistence.models_pnl import PaperTradePnL
from src.backend.services.persistence.models_paper import PaperTradeSnapshot

class PnLSimulator:
    """
    Engine determinístico para cálculo de PnL de Arbitragem.
    Configurado para cenário conservador (Worst Case Fees/Funding).
    """

    def __init__(
        self,
        taker_fee_pct: float = 0.0006,  # 0.06%
        maker_fee_pct: float = 0.0002,  # 0.02%
        funding_rate_hourly_avg: float = 0.0001 # 0.01% hora
    ):
        self.taker_fee_pct = taker_fee_pct
        self.funding_rate_hourly = funding_rate_hourly_avg

    def simulate(self, snapshot: PaperTradeSnapshot, exit_spot: float, exit_futures: float, close_time: datetime) -> PaperTradePnL:
        
        # 1. Definição de Quantidade (Baseada no capital de entrada)
        # CORREÇÃO: Usando 'spot_price' conforme schema oficial
        qty_asset = snapshot.capital_usd / snapshot.spot_price

        # 2. Cálculo do PnL Bruto (Mecânica da Arbitragem Long Spot / Short Futures)
        # Long Spot: (Preço Saída - Preço Entrada)
        pnl_spot = (exit_spot - snapshot.spot_price) * qty_asset
        
        # Short Futures: (Preço Entrada - Preço Saída)
        pnl_futures = (snapshot.futures_price - exit_futures) * qty_asset
        
        gross_pnl = pnl_spot + pnl_futures

        # 3. Cálculo de Custos (Fees)
        # Notional Total = Entrada (2 pernas) + Saída (2 pernas)
        total_volume_traded = (snapshot.capital_usd * 2) + ((exit_spot * qty_asset) + (exit_futures * qty_asset))
        fees = total_volume_traded * self.taker_fee_pct

        # 4. Cálculo de Funding
        duration = close_time - snapshot.timestamp
        hours_held = max(duration.total_seconds() / 3600, 0.01)
        
        # Funding rate paga sobre o notional de futuros
        funding_cost = (snapshot.futures_price * qty_asset) * self.funding_rate_hourly * hours_held

        # 5. Resultado Líquido
        net_pnl = gross_pnl - fees - funding_cost
        roi_pct = (net_pnl / snapshot.capital_usd) * 100

        return PaperTradePnL(
            snapshot_id=snapshot.id,
            symbol=snapshot.symbol,
            capital_usd=snapshot.capital_usd,
            
            exit_spot_price=exit_spot,
            exit_futures_price=exit_futures,
            
            fees_total_usd=round(fees, 4),
            funding_total_usd=round(funding_cost, 4),
            
            gross_pnl_usd=round(gross_pnl, 4),
            net_pnl_usd=round(net_pnl, 4),
            net_pnl_pct=round(roi_pct, 4),
            
            holding_seconds=int(duration.total_seconds()),
            timestamp_close=close_time
        )