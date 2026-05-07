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
            async with session.get(f"{BASE_URL}profiles/{telegram_id}/") as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logging.error(f"Profil xatosi: {e}")
            return None


async def get_orders(telegram_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}buyurtmalar/{telegram_id}/") as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logging.error(f"Buyurtma xatosi: {e}")
            return []


async def get_products_by_category(cat_id):


    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}mahsulotlar/", timeout=10) as response:
                if response.status != 200:
                    logging.error(f"API xatosi: Status {response.status}")
                    return []

                all_products = await response.json()

                filtered_products = []
                for product in all_products:

                    category_data = product.get('kategoriya') or product.get('category')

                    if category_data is None:
                        continue

                    if isinstance(category_data, dict):
                        prod_cat_id = category_data.get('id')
                    else:
                        prod_cat_id = category_data

                    if str(prod_cat_id) == str(cat_id):
                        filtered_products.append(product)

                logging.info(f"Kategoriya {cat_id} bo'yicha {len(filtered_products)} ta mahsulot topildi.")
                return filtered_products

        except Exception as e:
            logging.error(f"Mahsulotlarni olishda jiddiy xato: {e}")
            return []