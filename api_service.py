import aiohttp
import logging
from config import BASE_URL

class APIService:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status in (200, 201):
                    return await response.json()

                text = await response.text()
                logging.error(f"[API ERROR] {response.status} {url} -> {text}")
                return None

        except Exception as e:
            logging.exception(f"[CONNECTION ERROR] {url} -> {e}")
            return None

    async def get_categories(self):
        return await self._request("GET", "kategoriyalar/") or []

    async def get_products_by_category(self, cat_id):
        # BEST PRACTICE: backend filter bo'lishi kerak
        return await self._request("GET", f"products/?category={cat_id}") or []

    async def get_profile(self, telegram_id):
        return await self._request("GET", f"profile/{telegram_id}/")

    async def get_orders(self, telegram_id):
        return await self._request("GET", f"orders/{telegram_id}/") or []

    
    async def create_order(self, data):
        return await self._request("POST", "orders/", json=data)