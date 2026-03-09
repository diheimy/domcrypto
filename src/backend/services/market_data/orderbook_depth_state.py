import logging
from typing import List
from src.backend.services.market_data.orderbook_depth_state import OrderBookDepthState
from src.backend.services.fetch.exchange_fetcher import ExchangeFetcher

logger = logging.getLogger("OrderBookFetcher")

class OrderBookFetcher:
    """
    Sensor de Order Book especializado.
    Usa o ExchangeFetcher (Singleton) para acesso à API
    e escreve no OrderBookDepthState (Singleton/Shared).
    """

    def __init__(self, state: OrderBookDepthState):
        self.state = state
        self.fetcher = ExchangeFetcher() # Reusa conexões existentes

    async def fetch_and_update(self, symbols: List[str]):
        """
        Busca livros e atualiza o estado compartilhado.
        """
        # Delega o I/O pesado para o ExchangeFetcher (que já tem o método fetch_books da etapa anterior)
        # Se não tiver, usamos a lógica aqui, mas acessando self.fetcher.binance
        
        # Otimização: O ExchangeFetcher já implementou fetch_books na Etapa 2.1?
        # Se sim, usamos ele. Se não, implementamos a lógica de fetch aqui usando as conexões dele.
        # Assumindo que o ExchangeFetcher é a porta de saída:
        
        books_data = await self.fetcher.fetch_books(symbols)

        for key, data in books_data.items():
            # key format: SYMBOL_Exchange (vindo do ExchangeFetcher)
            try:
                if "_" in key:
                    symbol, exchange = key.split("_")
                    
                    self.state.update(
                        exchange=exchange,
                        symbol=symbol,
                        bid_liquidity_usd=data.get("bid_usd", 0.0),
                        ask_liquidity_usd=data.get("ask_usd", 0.0)
                    )
            except Exception as e:
                logger.warning(f"Erro ao processar book {key}: {e}")