import asyncio
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv


def setup_bot():
    dp.include_router(router)

load_dotenv()

TOKEN = os.getenv("8701385504:AAGATjB5tyQNdoifS-VaOJ8pNRb7DwFRRzg")
API_URL = os.getenv("DJANGO_HOST") + "/api"

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Salom 👋 Production bot ishlayapti!")


@dp.message(Command("products"))
async def products(msg: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL + "/products/") as resp:
            data = await resp.json()

    text = "🛒 Mahsulotlar:\n\n"
    for p in data:
        text += f"📦 {p['name']} - {p['price']}\n"

    await msg.answer(text)


async def main():
    print("BOT START 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())