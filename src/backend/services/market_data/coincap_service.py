import aiohttp
import logging
import asyncio

logger = logging.getLogger("CoinCapService")

class CoinCapService:
    BASE_URL = "https://api.coincap.io/v2"

    async def get_spot_prices(self):
        """
        Fetches top 100 assets from CoinCap to serve as Spot Reference.
        Returns a dictionary: {'BTC': {'price': 50000.0, 'volume': 1000000000}, ...}
        """
        url = f"{self.BASE_URL}/assets?limit=100"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {}
                        for item in data['data']:
                            symbol = item['symbol'].upper()
                            try:
                                price = float(item['priceUsd'])
                                volume = float(item['volumeUsd24Hr'] or 0)
                                
                                # Format used by OpportunityBuilder
                                result[symbol] = {
                                    'last': price,
                                    'ask': price * 1.0005, # Simulates a small spread for spot reference
                                    'bid': price * 0.9995,
                                    'volume': volume,
                                    'quoteVolume': volume # Proxy
                                }
                            except (ValueError, TypeError):
                                continue
                        
                        # logger.info(f"✅ CoinCap: {len(result)} spot prices updated.")
                        return {'coincap': result} # Structure compatible with builder
                    else:
                        logger.error(f"❌ CoinCap Error: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"❌ CoinCap Connection Failed: {e}")
            return {}