import aiohttp
from decimal import Decimal

class DeribitClient:

    BASE_URL = "https://test.deribit.com/api/v2/public"

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_index_price(self, index_name) -> Decimal:
        url = f"{self.BASE_URL}/get_index_price" 
        async with self.session.get(url, params={"index_name": index_name}) as response:
            response.raise_for_status()
            data = await response.json()
        try:
            return Decimal(data['result']['index_price'])
        except KeyError:
            raise ValueError(f"Unexpected response: {data}")
