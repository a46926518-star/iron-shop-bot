import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = "8701385504:AAE4qIhBWy82KHdqHnpJq0z3vcbzpFHM-Fo"
API_URL = "https://xxxx.ngrok.io/api/"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Salom 👋\nMahsulotlarni ko‘rish uchun /products yozing")


@dp.message(Command("products"))
async def products(msg: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL + "products/") as resp:
            data = await resp.json()

            text = "🛒 Mahsulotlar:\n\n"
            for p in data:
                text += f"📦 {p['name']} - {p['price']} so'm\n"

            await msg.answer(text)

@dp.message(Command("order"))
async def order(msg: Message):
    try:
        parts = msg.text.split()

        if len(parts) < 2:
            await msg.answer("❗ Misol: /order 1 2 3")
            return

        product_ids = list(map(int, parts[1:]))

        data = {
            "product_ids": product_ids,
            "full_name": msg.from_user.full_name,
            "phone_number": "unknown"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL + "order/create/", json=data) as resp:
                result = await resp.json()

        await msg.answer(
            f"✅ Buyurtma yaratildi!\n"
            f"🆔 ID: {result['order_id']}\n"
            f"💰 Summa: {result['total']}"
        )

    except Exception as e:
        await msg.answer(f"❌ Xatolik: {str(e)}")