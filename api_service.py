import aiohttp
import logging
from config import BASE_URL

async def get_categories():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}kategoriyalar/") as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logging.error(f"Katalog xatosi: {e}")
            return []

async def get_profile(telegram_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}profile/{telegram_id}/") as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logging.error(f"Profil xatosi: {e}")
            return None

async def get_orders(telegram_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}orders/{telegram_id}/") as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logging.error(f"Buyurtma xatosi: {e}")
            return []

async def get_products_by_category(cat_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}products/") as response:
                if response.status == 200:
                    all_products = await response.json()
                    filtered_products = [
                        p for p in all_products
                        if str(p.get('category')) == str(cat_id)
                    ]
                    return filtered_products
                return []
        except Exception as e:
            logging.error(f"Mahsulot xatosi: {e}")
            return []