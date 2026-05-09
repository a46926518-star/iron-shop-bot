import os
import asyncio
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

import keyboards as kb
from api_service import APIService
from config import BOT_TOKEN, DJANGO_HOST, ADMIN_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
api = APIService()

async def handle(request):
    return web.Response(text="Bot is running!", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 4000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    logger.info(f"🌐 Web server {port}-portda ishga tushdi")
    await site.start()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        categories = await api.get_categories()

        # Bu yerga do'koningizning chiroyli logotipi yoki rasmi linkini qo'ying
        welcome_photo = "https://your-image-link.com/photo.jpg"

        welcome_text = (
            f"👋 Salom, <b>{message.from_user.full_name}</b>!\n\n"
            f"🏢 <b>Iron Shop</b> do'konimizga xush kelibsiz.\n"
            f"Biz bilan sifatli metall mahsulotlarini onlayn buyurtma qiling.\n\n"
            f"🛍 <b>Kategoriyani tanlang:</b>"
        )

        await message.answer_photo(
            photo=welcome_photo,
            caption=welcome_text,
            reply_markup=kb.categories_kb(categories)
        )
    except Exception as e:
        logger.error(f"START ERROR: {e}")
        await message.answer("❌ Xatolik yuz berdi")

@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    try:
        cat_id = callback.data.split("_")[1]
        products = await api.get_products_by_category(cat_id)

        if not products:
            await callback.answer("Mahsulot yo‘q ❌", show_alert=True)
            return

        for p in products:
            caption = f"<b>{p.get('name')}</b>\n💰 {p.get('price')} $"
            img = p.get("image")
            if img and not img.startswith("http"):
                img = f"{DJANGO_HOST}{img}"

            markup = kb.buy_product_kb(p["id"])
            if img:
                await callback.message.answer_photo(img, caption=caption, reply_markup=markup)
            else:
                await callback.message.answer(caption, reply_markup=markup)
        await callback.answer()
    except Exception as e:
        logger.error(f"PRODUCT ERROR: {e}")
        await callback.answer("Xatolik ❌", show_alert=True)

@dp.callback_query(F.data.startswith("buy_"))
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]
    await state.update_data(product_id=product_id)
    await callback.message.answer("📝 Ismingizni kiriting:")
    await state.set_state(OrderState.waiting_for_name)
    await callback.answer()

@dp.message(OrderState.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=kb.contact_markup())
    await state.set_state(OrderState.waiting_for_phone)


@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        phone = message.contact.phone_number if message.contact else message.text


        order_data = {
            "product_id": data["product_id"],
            "name": data["name"],
            "phone": phone,
            "telegram_id": message.from_user.id
        }

        await api.create_order(order_data)

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 <b>Yangi buyurtma!</b>\n\n👤 Ism: {data['name']}\n📞 Tel: {phone}\n📦 Product ID: {data['product_id']}"
        )

        confirmation_text = (
            f"✅ <b>Sizning buyurtmangiz qabul qilindi!</b>\n\n"
            f"👤 <b>Ism:</b> {data['name']}\n"
            f"📞 <b>Telefon:</b> {phone}\n"
            f"📦 <b>Mahsulot:</b> #{data['product_id']}\n\n"
            f"⏳ Tez orada operatorimiz siz bilan bog'lanadi."
        )

        await message.answer(confirmation_text, reply_markup=kb.main_menu)
        await state.clear()

    except Exception as e:
        logger.error(f"ORDER ERROR: {e}")
        await message.answer("❌ Buyurtma xatoligi yuz berdi")
@dp.message(F.text == "📂 Katalog")
async def catalog(message: types.Message):
    categories = await api.get_categories()
    await message.answer("🛍 Kategoriya tanlang:", reply_markup=kb.categories_kb(categories))

@dp.message(F.text == "👤 Profilim")
async def profile(message: types.Message):
    await message.answer(f"👤 Ism: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}")

@dp.message(F.text == "ℹ️ Ma'lumot")
async def info(message: types.Message):
    await message.answer("🏪 Iron Shop — sifatli mahsulotlar do‘koni")

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("📞 Admin: @yosh_admin")

async def main():
    await api.start()
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🚀 Bot polling rejimida ishga tushdi")
    try:
        await dp.start_polling(bot)
    finally:
        await api.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🤖 Bot to'xtatildi")