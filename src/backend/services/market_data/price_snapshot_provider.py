from src.backend.pipeline.normalizer import normalize_exchange_data

class PriceSnapshotProvider:
    """
    Fornece o preço ATUAL de mercado para um símbolo específico.
    Em V2, isso encapsula a complexidade de buscar dados atualizados.
    """

    def __init__(self, fetcher):
        self.fetcher = fetcher

    async def get_prices(self, symbol: str):
        """
        Busca dados frescos e retorna (spot_price, futures_price) para o símbolo.
        Retorna (None, None) se não encontrar.
        """
        # 1. Busca dados brutos de todas as exchanges
        # (Em produção, isso seria otimizado para buscar só o símbolo, mas para V2 reutilizamos o fetcher)
        raw_data = await self.fetcher.fetch_all()
        
        if not raw_data:
            return None, None

        # 2. Normaliza para encontrar o par Spot/Futuros correto
        opportunities = normalize_exchange_data(raw_data)
        
        # 3. Filtra pelo símbolo desejado
        target_op = next((op for op in opportunities if op.symbol == symbol), None)
        
        if target_op:
            return target_op.spot_price, target_op.futures_price
            
        return None, None