import aiohttp
import logging
from config import BASE_URL

class APIService:
    def __init__(self):
        self.base_url = BASE_URL

    async def _get_request(self, endpoint):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        return await response.json()
                    logging.error(f"API Error {response.status}: {endpoint}")
                    return None
            except Exception as e:
                logging.error(f"Connection Error: {e}")
                return None

    async def get_categories(self):
        result = await self._get_request("kategoriyalar/")
        return result if result else []

    async def get_products_by_category(self, cat_id):
        all_products = await self._get_request("products/")
        if all_products:
            return [p for p in all_products if str(p.get('category')) == str(cat_id)]
        return []

    async def get_profile(self, telegram_id):
        return await self._get_request(f"profile/{telegram_id}/")

    async def get_orders(self, telegram_id):
        result = await self._get_request(f"orders/{telegram_id}/")
        return result if result else []

api = APIService()