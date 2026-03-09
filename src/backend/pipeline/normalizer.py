import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger("Normalizer")

# Definição local da classe para garantir consistência neste arquivo
class Opportunity:
    def __init__(self, symbol, ex_spot, ex_fut, price_spot, price_fut, vol):
        self.symbol = symbol
        self.exchange_spot = ex_spot
        self.exchange_futures = ex_fut
        self.spot_price = float(price_spot)
        self.futures_price = float(price_fut)
        
        # Atributo oficial para DTO v1
        self.volume_24h_usd = float(vol)
        
        # Cálculos básicos
        if self.spot_price > 0:
            self.spread_pct = ((self.futures_price - self.spot_price) / self.spot_price) * 100
        else:
            self.spread_pct = 0.0
            
        self.spread_net_pct = 0.0 
        self.score = 0.0
        self.tags = []
        self.health_score = 100.0
        self.status = "OBSERVED"

def clean_symbol_name(symbol: str) -> str:
    """
    Limpa o símbolo para obter apenas o ATIVO BASE.
    Ex: 'BTC/USDT' -> 'BTC'
    Ex: 'FLOWUSDT' -> 'FLOW'
    """
    # 1. Remove barras
    s = symbol.replace('/', '')
    
    # 2. Remove sufixos de futuros (ex: :USDT, -240329)
    s = re.split(r'[:\-]', s)[0]
    
    s = s.upper()
    
    # 3. CORREÇÃO DE REDUNDÂNCIA:
    # Se o nome terminar com USDT, removemos para ficar só a base.
    # Evita: FLOWUSDT/USDT
    if s.endswith('USDT'):
        s = s[:-4]
        
    return s

def normalize_exchange_data(raw_data: Dict[str, Any]) -> List[Opportunity]:
    opportunities = []
    parsed_markets = {} 
    
    # 1. Parsing
    for ex_id, tickers in raw_data.items():
        if not tickers: continue
        
        parts = ex_id.split('_')
        base_name = parts[0]
        market_type = parts[1]
        
        for symbol, ticker in tickers.items():
            if 'USDT' not in symbol: continue
            
            # Agora retorna limpo (Ex: FLOW)
            clean_sym = clean_symbol_name(symbol)
            
            # Se o clean falhar e retornar vazio, pula
            if not clean_sym: continue
            
            if clean_sym not in parsed_markets:
                parsed_markets[clean_sym] = {'spots': [], 'futures': []}
            
            try:
                price = float(ticker.get('last') or ticker.get('close') or 0)
                vol = float(ticker.get('quoteVolume') or ticker.get('baseVolume') or 0)
                
                # Conversão bruta de volume base -> quote se necessário
                if vol < 10000 and price > 0: 
                    vol = vol * price

                data_point = {
                    'exchange': base_name,
                    'price': price,
                    'volume': vol
                }
                
                if price > 0:
                    if market_type == 'spot':
                        parsed_markets[clean_sym]['spots'].append(data_point)
                    else:
                        parsed_markets[clean_sym]['futures'].append(data_point)
            except Exception:
                continue

    # 2. Matching
    for symbol, markets in parsed_markets.items():
        spots = markets['spots']
        futures = markets['futures']
        
        if not spots or not futures: continue
        
        for spot in spots:
            for fut in futures:
                # Cria a oportunidade
                # symbol aqui já é puro (ex: FLOW), então o resultado é FLOW/USDT
                op = Opportunity(
                    symbol=f"{symbol}/USDT", 
                    ex_spot=spot['exchange'],
                    ex_fut=fut['exchange'],
                    price_spot=spot['price'],
                    price_fut=fut['price'],
                    vol=spot['volume'] 
                )
                
                opportunities.append(op)

    return opportunities