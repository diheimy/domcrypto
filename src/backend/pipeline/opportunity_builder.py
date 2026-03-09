import logging
import copy
import re
from src.backend.models.opportunity import Opportunity
from src.backend.services.execution.depth_calculator import DepthCalculator
from src.backend.config.settings import ESTIMATED_TOTAL_FEE 

logger = logging.getLogger('OpportunityBuilder')

class OpportunityBuilder:
    
    # --- CONSTANTES INSTITUCIONAIS ---
    
    # Filtro de Volume: Abaixo disso, o par é DESCARTADO (Hard Filter)
    MIN_VOL_24H_USD = 50000.0  
    
    # Guardas de Preço (Rigorosos)
    MAX_PRICE_RATIO = 5.0  
    MIN_PRICE_RATIO = 1.0 / MAX_PRICE_RATIO
    
    # Spread Absurdo: Se passar de 50%, marcamos como OBSERVATION_ONLY
    MAX_VALID_SPREAD_PCT = 50.0 

    # [FIX COLISÃO] Whitelist de multiplicadores
    VALID_MULTIPLIERS = [10, 100, 1000, 10000, 100000, 1000000]
    
    # Blacklist de Bases
    IGNORED_BASES = {'USDT', 'USDC', 'USD', 'BUSD', 'DAI', 'FDUSD', 'TUSD', 'EUR', 'GBP'}
    
    # Stablecoins confiáveis para cálculo de Volume
    STABLE_QUOTES = {'USDT', 'USDC', 'USD', 'BUSD', 'DAI', 'FDUSD', 'TUSD', 'USDD', 'USDP'}

    @staticmethod
    def _extract_base_quote_mult(raw_symbol: str):
        """
        Realiza o parsing SEMÂNTICO e ESTRUTURAL do símbolo.
        Retorna: (clean_base, clean_quote, multiplier_from_symbol, is_valid)
        """
        if not raw_symbol: return '', '', 1, False
        
        # 1. Limpeza preliminar
        s = raw_symbol.split(':')[0]
        s = s.replace('PERP', '').replace('SWAP', '')
        
        # 2. Separação Base / Quote
        base_raw = ''
        quote_raw = 'USDT'
        
        if '/' in s:
            parts = s.split('/')
            base_raw = parts[0]
            if len(parts) > 1: quote_raw = parts[1]
        elif '-' in s:
            parts = s.split('-')
            base_raw = parts[0]
            if len(parts) > 1: quote_raw = parts[1]
        elif '_' in s:
            parts = s.split('_')
            base_raw = parts[0]
            if len(parts) > 1: quote_raw = parts[1]
        else:
            if s.endswith('USDT'): base_raw = s[:-4]; quote_raw = 'USDT'
            elif s.endswith('USDC'): base_raw = s[:-4]; quote_raw = 'USDC'
            elif s.endswith('USD'): base_raw = s[:-3]; quote_raw = 'USD'
            else: base_raw = s 
        
        # 3. Normalização
        base_clean = base_raw.upper().replace('-', '').replace('_', '')
        quote_clean = quote_raw.upper().replace('-', '').replace('_', '')
        
        # Normalização de Quote Variável
        if quote_clean.startswith('USDT'): quote_clean = 'USDT'
        if quote_clean.startswith('USDC'): quote_clean = 'USDC'
        if quote_clean.startswith('USD') and quote_clean != 'USDC': quote_clean = 'USD'
        
        # 4. Filtros de Qualidade
        if base_clean in OpportunityBuilder.IGNORED_BASES: return base_clean, quote_clean, 1, False
        if base_clean == quote_clean: return base_clean, quote_clean, 1, False
        if not base_clean: return '', '', 1, False

        # 5. Extração de Multiplicador do SÍMBOLO
        multiplier = 1
        match = re.match(r'^(\d+)([A-Z0-9]+)$', base_clean)
        if match:
            mult_str = match.group(1)
            remaining_base = match.group(2)
            try:
                m_val = int(mult_str)
                if m_val in OpportunityBuilder.VALID_MULTIPLIERS:
                    multiplier = m_val
                    base_clean = remaining_base
            except Exception: pass # Adicionado except
            
        return base_clean, quote_clean, multiplier, True

    @staticmethod
    def _get_ticker_multiplier_candidate(ticker):
        """
        Extrai um candidato a multiplicador dos metadados do ticker.
        Sanitiza strings como "1,000".
        """
        try:
            # 1. Chaves diretas
            direct_keys = ['contractSize', 'multiplier', 'sizeMultiplier', 'ctVal']
            for k in direct_keys:
                if k in ticker and ticker[k]:
                    try:
                        val_str = str(ticker[k]).replace(',', '')
                        val = float(val_str)
                        if val > 1: return val
                    except Exception: continue # Adicionado except
            
            # 2. Chaves dentro de 'info'
            info = ticker.get('info', {})
            if isinstance(info, dict):
                info_keys = ['sizeMultiplier', 'contractSize', 'multiplier', 'lotSize']
                for k in info_keys:
                    if k in info and info[k]:
                        try:
                            val_str = str(info[k]).replace(',', '')
                            val = float(val_str)
                            if val > 1: return val
                        except Exception: continue # Adicionado except
        except Exception: pass # Adicionado except
        return 1.0

    @staticmethod
    def _get_price(ticker, kind='ask'):
        keys = ['ask', 'lowestAsk', 'askPrice', 'bestAsk', 'close'] if kind == 'ask' else ['bid', 'highestBid', 'bidPrice', 'bestBid', 'close']
        for k in keys:
            val = ticker.get(k)
            if val is not None:
                try:
                    f_val = float(val)
                    if f_val > 0: return f_val
                except Exception: continue # Adicionado except
        return 0.0

    @staticmethod
    def _get_volume_usd(ticker, price_unit, quote_asset, is_future=False, multiplier=1.0):
        """
        Calcula volume financeiro com inteligência de contrato.
        [V13 Enhanced] Varre chaves específicas da Bitget/Bybit para evitar descarte indevido.
        """
        # 1. Tenta Quote Volume (Prioridade)
        # Se for Stable OU se for Futuros com Multiplicador, tenta pegar quote volume direto
        has_risk_of_contracts = (is_future and multiplier > 1)
        force_quote = (quote_asset in OpportunityBuilder.STABLE_QUOTES) or has_risk_of_contracts
        
        q_val = 0.0
        
        # Lista expandida de chaves padrão
        q_keys = ['quoteVolume', 'quoteVol', 'quote_volume', 'volumeQuote', 'volume24', 'turnover', 'value', 'money']
        for k in q_keys:
            val = ticker.get(k)
            if val is not None:
                try:
                    v = float(val)
                    if v > 0: 
                        q_val = v
                        break
                except Exception: continue # Adicionado except
        
        # Se não achou, Deep Search no 'info' (Bitget fix)
        if q_val == 0:
            info = ticker.get('info', {})
            if isinstance(info, dict):
                # Chaves específicas de exchanges asiáticas e derivativos
                raw_keys = [
                    'quoteVol', 'usdtVolume', 'turnover_24h', 'volume_24h', 
                    'usdtTurnover', 'quoteTurnover', 'turnoverValue', 'value_24h'
                ]
                for k in raw_keys:
                    if k in info and info[k]:
                        try:
                            v = float(str(info[k]))
                            if v > 0:
                                q_val = v
                                break
                        except Exception: continue # Adicionado except

        # Se encontrou Quote Volume, retorna imediatamente.
        if q_val > 0:
            return q_val

        # Se não achou quote volume, mas TEM risco de contratos (f_m > 1), aborta.
        # Retorna 0.0 para ser capturado como "Untrusted Volume"
        if has_risk_of_contracts:
            return 0.0 

        # 2. Fallback: Base * Unit Price (Apenas para Spot ou Futuros 1:1)
        b_keys = ['baseVolume', 'base_volume', 'volume', 'vol', 'baseVol']
        for k in b_keys:
            val = ticker.get(k)
            if val is not None:
                try:
                    v = float(val)
                    if v > 0 and price_unit > 0: 
                        return v * price_unit 
                except Exception: continue # Adicionado except
        
        return 0.0

    @staticmethod
    def _get_depth(ticker, kind='asks'):
        possible_keys = [f'{kind}_depth', kind, f'{kind}Book']
        for k in possible_keys:
            val = ticker.get(k)
            if val and isinstance(val, list) and len(val) > 0: return val
        
        book_container = ticker.get('book')
        if isinstance(book_container, dict):
            val = book_container.get(kind)
            if val and isinstance(val, list): return val
        return []

    @staticmethod
    def _get_ticker_size_fallback(ticker, kind='ask'):
        standard_keys = ['askVolume', 'askSize', 'askAmount'] if kind == 'ask' else ['bidVolume', 'bidSize', 'bidAmount']
        for k in standard_keys:
            val = ticker.get(k)
            if val is not None:
                try: return float(val)
                except Exception: continue # Adicionado except
        return 0.0

    @staticmethod
    def build_batch(spot_data, futures_data):
        opportunities = []
        
        # Telemetria V13
        stats = {
            'gen': 0, 
            'scale_err': 0, 
            'absurd': 0, 
            'fee_block': 0, 
            'skip_low_vol': 0, 
            'skip_untrusted': 0, # Descarte por falta de dados confiáveis em contratos
            'proc_err': 0,
            'mult_accept': 0,
            'mult_reject': 0
        }
        
        try:
            if not spot_data or not futures_data: return []

            # -------------------------------------------------------
            # 1. INDEXAÇÃO POR (BASE, QUOTE)
            # -------------------------------------------------------
            norm_spot = {}
            for exch_name, tickers in spot_data.items():
                for sym, ticker in tickers.items():
                    try:
                        base, quote, mult, valid = OpportunityBuilder._extract_base_quote_mult(sym)
                        if not valid: continue 
                        key = (base, quote)
                        if key not in norm_spot: norm_spot[key] = []
                        norm_spot[key].append( (exch_name, sym, ticker, mult) )
                    except Exception as e: # Adicionado except para o try interno
                        logger.warning(f"Error processing spot ticker {sym} from {exch_name}: {e}")
                        continue

            norm_fut = {}
            for exch_name, tickers in futures_data.items():
                for sym, ticker in tickers.items():
                    try:
                        base, quote, mult, valid = OpportunityBuilder._extract_base_quote_mult(sym)
                        if not valid: continue
                        key = (base, quote)
                        if key not in norm_fut: norm_fut[key] = []
                        norm_fut[key].append( (exch_name, sym, ticker, mult) )
                    except Exception as e: # Adicionado except para o try interno
                        logger.warning(f"Error processing futures ticker {sym} from {exch_name}: {e}")
                        continue

            # -------------------------------------------------------
            # 2. MATCHING & CÁLCULO
            # -------------------------------------------------------
            for (base_sym, quote_sym), spot_list in norm_spot.items():
                if (base_sym, quote_sym) in norm_fut:
                    fut_list = norm_fut[(base_sym, quote_sym)]
                    
                    for (s_exch, s_real_sym, s_ticker, s_symbol_mult) in spot_list:
                        for (f_exch, f_real_sym, f_ticker, f_symbol_mult) in fut_list:
                            try:
                                # A. Detectar Multiplicadores
                                s_m = float(s_symbol_mult) if s_symbol_mult > 1 else 1.0
                                
                                spot_ask_raw = OpportunityBuilder._get_price(s_ticker, "ask")
                                best_fut_bid_raw = OpportunityBuilder._get_price(f_ticker, "bid")
                                if spot_ask_raw <= 0 or best_fut_bid_raw <= 0: continue

                                f_m = 1.0
                                candidate_accepted = False
                                
                                if f_symbol_mult > 1:
                                    f_m = float(f_symbol_mult)
                                else:
                                    cand_m = OpportunityBuilder._get_ticker_multiplier_candidate(f_ticker)
                                    if cand_m > 1:
                                        # Ratio Test
                                        spot_unit_temp = spot_ask_raw / s_m
                                        fut_unit_temp = best_fut_bid_raw / cand_m
                                        if spot_unit_temp > 0:
                                            ratio_temp = fut_unit_temp / spot_unit_temp
                                            if OpportunityBuilder.MIN_PRICE_RATIO <= ratio_temp <= OpportunityBuilder.MAX_PRICE_RATIO:
                                                f_m = cand_m
                                                stats['mult_accept'] += 1
                                                candidate_accepted = True
                                            else:
                                                stats['mult_reject'] += 1

                                # B. Preços Unitários Finais
                                spot_price_unit = spot_ask_raw / s_m
                                fut_price_unit = best_fut_bid_raw / f_m
                                if spot_price_unit == 0: continue

                                # C. Guardas de Escala
                                ratio = fut_price_unit / spot_price_unit
                                is_scale_error = False
                                if ratio < OpportunityBuilder.MIN_PRICE_RATIO or ratio > OpportunityBuilder.MAX_PRICE_RATIO:
                                    is_scale_error = True
                                    stats['scale_err'] += 1

                                # D. Spread
                                spread_exec_pct = ((fut_price_unit - spot_price_unit) / spot_price_unit) * 100
                                fees_total_pct = ESTIMATED_TOTAL_FEE
                                spread_net_pct = spread_exec_pct - fees_total_pct
                                spread_net_usd = (spread_net_pct / 100.0) * spot_price_unit

                                is_absurd_spread = False
                                if abs(spread_exec_pct) > OpportunityBuilder.MAX_VALID_SPREAD_PCT:
                                    is_absurd_spread = True
                                    stats['absurd'] += 1

                                # E. Volume & STRICT FILTER
                                vol_s = OpportunityBuilder._get_volume_usd(s_ticker, spot_price_unit, quote_sym, False, s_m)
                                vol_f = OpportunityBuilder._get_volume_usd(f_ticker, fut_price_unit, quote_sym, True, f_m)
                                volume_24h = max(vol_s, vol_f)
                                
                                if volume_24h < OpportunityBuilder.MIN_VOL_24H_USD:
                                    # Diagnóstico de descarte
                                    if volume_24h == 0 and f_m > 1:
                                        stats['skip_untrusted'] += 1 # Risco de contratos sem quoteVol
                                    else:
                                        stats['skip_low_vol'] += 1
                                    continue 

                                # F. Criação do Objeto
                                op = Opportunity(
                                    symbol=f"{base_sym}/{quote_sym}", 
                                    exchange_spot=s_exch,
                                    exchange_futures=f_exch,
                                    spot_price=spot_price_unit,
                                    futures_price=fut_price_unit
                                )
                                
                                # G. Tags e Status
                                if s_m > 1: op.tags.append(f"MULT_SPOT:{int(s_m)}x")
                                if f_m > 1: op.tags.append(f"MULT_FUT:{int(f_m)}x")
                                if candidate_accepted: op.tags.append("MULT_CAND_ACCEPTED")
                                
                                if is_scale_error: 
                                    op.tags.append("INVALID_PRICE_SCALE")
                                    if candidate_accepted: op.tags.append("POST_MULT_RATIO_FAIL")
                                    op.status = "OBSERVATION_ONLY"
                                elif is_absurd_spread:
                                    op.tags.append("ABSURD_SPREAD")
                                    op.status = "OBSERVATION_ONLY"
                                elif spread_net_pct <= 0:
                                    op.tags.append("FEE_BLOCKED")
                                    op.status = "OBSERVATION_ONLY"
                                    stats['fee_block'] += 1
                                else:
                                    op.status = "ACTIVE"
                                
                                if s_exch == f_exch: op.tags.append("SAME_VENUE")
                                else: op.tags.append("CROSS_VENUE")

                                op.spread_pct = spread_exec_pct
                                op.spread_exec_pct = spread_exec_pct
                                op.spread_net_pct = spread_net_pct
                                op.fees_total_pct = fees_total_pct
                                op.spread_net_usd = spread_net_usd
                                op.volume_24h_usd = volume_24h

                                # ================================
                                # V113 - Price Range (usando spread atual como baseline)
                                # ================================
                                # Inicializa range com valores do spread atual
                                op.range_low = spread_exec_pct
                                op.range_high = spread_exec_pct
                                op.range_basis = "spread_exec_pct"
                                op.range_pct = 0.0

                                # ================================
                                # V113 - Funding (converte pct para decimal)
                                # ================================
                                op.funding_rate = op.funding_rate_pct / 100.0 if op.funding_rate_pct else 0.0
                                # funding_interval_hours e next_funding_at mantêm defaults
                                # (podem ser atualizados pelo FundingEngine se disponível)

                                # H. Liquidez & Sanity
                                spot_book = OpportunityBuilder._get_depth(s_ticker, "asks")
                                fut_book = OpportunityBuilder._get_depth(f_ticker, "bids")
                                
                                s_top_usd = 0.0
                                f_top_usd = 0.0
                                
                                # Spot Liquidity
                                if spot_book:
                                    try: s_top_usd = spot_price_unit * float(spot_book[0][1])
                                    except Exception: pass # Adicionado except
                                elif vol_s > 0:
                                    s_top_usd = vol_s * 0.0005

                                # Spot Clamping (Safety)
                                if vol_s > 0 and s_top_usd > (vol_s * 0.20):
                                    s_top_usd = vol_s * 0.02
                                    if spot_book: op.tags.append("TOP_LIQ_CLAMPED_FROM_BOOK")
                                    else: op.tags.append("TOP_LIQ_CLAMPED_EST")

                                # Futures Liquidity
                                if fut_book and f_m == 1:
                                    try: f_top_usd = fut_price_unit * float(fut_book[0][1])
                                    except Exception: pass # Adicionado except
                                elif vol_f > 0:
                                    f_top_usd = vol_f * 0.0005 
                                    
                                op.spot_top_book_usd = s_top_usd
                                op.futures_top_book_usd = f_top_usd
                                op.top_liquidity_usd = min(s_top_usd, f_top_usd) if s_top_usd>0 and f_top_usd>0 else max(s_top_usd, f_top_usd)
                                op.top_liquidity_avg = op.top_liquidity_usd

                                # I. Depth Calculation
                                if not is_scale_error and not is_absurd_spread:
                                    try:
                                        if op.entry_leg_usd <= 0:
                                            op.depth_exec_usd = 0
                                            op.spot_px_start = 0.0
                                            op.spot_px_limit = 0.0
                                            op.fut_px_start = 0.0
                                            op.fut_px_limit = 0.0
                                            op.orders_to_fill_spot = 0
                                            op.orders_to_fill_fut = 0
                                            op.orders_to_fill_total = 0
                                            op.fill_status = "NO_DEPTH"
                                            op.tags.append("NO_CAPACITY_TO_SWEEP")
                                        elif spot_book and fut_book and f_m == 1 and s_m == 1:
                                            s_book_calc = copy.deepcopy(spot_book)
                                            f_book_calc = copy.deepcopy(fut_book)
                                            
                                            depth_result = DepthCalculator.calculate(
                                                s_book_calc, f_book_calc, usd_target=op.entry_leg_usd, fee_pct=fees_total_pct
                                            )

                                            op.spot_px_start = depth_result["spot"]["px_start"]
                                            op.spot_px_limit = depth_result["spot"]["px_limit"]
                                            op.fut_px_start = depth_result["fut"]["px_start"]
                                            op.fut_px_limit = depth_result["fut"]["px_limit"]
                                            op.orders_to_fill_spot = depth_result["spot"]["levels"]
                                            op.orders_to_fill_fut = depth_result["fut"]["levels"]
                                            op.orders_to_fill_total = op.orders_to_fill_spot + op.orders_to_fill_fut
                                            op.fill_status = depth_result["fill_status"]

                                            # Calculo da profundidade executável em USD
                                            # Usamos o mínimo entre as pernas preenchidas, se ambas foram preenchidas
                                            # ou o máximo se apenas uma foi parcialmente preenchida.
                                            if depth_result["spot"]["filled_usd"] > 0 and depth_result["fut"]["filled_usd"] > 0:
                                                op.depth_exec_usd = min(depth_result["spot"]["filled_usd"], depth_result["fut"]["filled_usd"])
                                            else:
                                                op.depth_exec_usd = max(depth_result["spot"]["filled_usd"], depth_result["fut"]["filled_usd"])

                                            op.depth_exec_levels = op.orders_to_fill_total
                                            
                                            # Se o fill_status não for OK, pode ser que o target não foi totalmente preenchido.
                                            if op.fill_status != "OK":
                                                op.tags.append(f"DEPTH_SWEEP_STATUS:{op.fill_status}")

                                            # Capacidade% = entry_leg / entry_max
                                            op.capacity_pct = entry_leg / op.entry_max_usd if op.entry_max_usd > 0 else 0

                                            # CapacityBand baseado na capacidade
                                            if op.capacity_pct >= 1.0:
                                                op.capacity_band = "GREEN"
                                                op.capacity_reason = "FULL"
                                            elif op.capacity_pct >= (op.entry_min_usd / op.entry_max_usd):
                                                op.capacity_band = "YELLOW"
                                                op.capacity_reason = "LIQUIDITY" if cap_max_leg < leg_budget else "BUDGET"
                                            else:
                                                op.capacity_band = "RED"
                                                op.capacity_reason = "NO_LIQUIDITY" if cap_max_leg < op.entry_min_usd else "MIN_NOT_MET"

                                            # ROI Net = spread_net_pct (já calculado)
                                            op.roi_net_pct = op.spread_net_pct if hasattr(op, "spread_net_pct") else 0

                                            # ProfitUsd = roi_net_pct/100 * entry_total_usd * 2
                                            entry_total = entry_leg * 2
                                            op.profit_usd = (op.roi_net_pct / 100) * entry_total if entry_total > 0 else 0
                                        else: # Se não houver books ou multiplicadores inválidos
                                            op.depth_exec_usd = 0
                                            op.tags.append("DEPTH_NO_BOOK_OR_MULT_ISSUE")
                                            op.fill_status = "NO_DEPTH"
                                    except Exception as e: 
                                        op.tags.append(f"DEPTH_CALC_ERROR: {e}")

                                opportunities.append(op)
                                stats["gen"] += 1
                                
                            except Exception as e:
                                stats["proc_err"] += 1
                                if stats["proc_err"] <= 5: 
                                    logger.warning(f"Row Error ({s_real_sym}/{f_real_sym}): {str(e)}")
                                continue
                            
        except Exception as e:
            logger.error(f"CRITICAL BUILDER ERROR: {str(e)}")
            return []

        if stats["gen"] > 0 or stats["proc_err"] > 0 or stats["skip_low_vol"] > 0:
            logger.info(f"🧮 BUILDER V13: Gen={stats['gen']}, SkipVol={stats['skip_low_vol']}, SkipUntrust={stats['skip_untrusted']}, MAcc={stats['mult_accept']}, MRej={stats['mult_reject']}, ScaleErr={stats['scale_err']}, Absurd={stats['absurd']}, FeeBlk={stats['fee_block']}")
        
        return sorted(opportunities, key=lambda x: x.spread_net_pct, reverse=True)
