import logging
import asyncio
import os
from aiohttp import web

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import keyboards as kb
import api_service as api
from config import TOKEN, DJANGO_HOST

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlari
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# Render serveri botni o'chirib qo'ymasligi uchun Web Server
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Darvoza Bot ishladi!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🌐 Web server {port}-portda ishlamoqda")


# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n"
        "Iron Shop sifatli darvozalar botiga xush kelibsiz.",
        reply_markup=kb.main_menu
    )


@dp.message(F.text == "🚪 Katalog")
async def show_categories(message: types.Message):
    data = await api.get_categories()
    if data:
        await message.answer("📁 <b>Kategoriyalardan birini tanlang:</b>", reply_markup=kb.build_categories_kb(data))
    else:
        await message.answer("📭 Hozircha katalog bo'sh yoki API bilan aloqa yo'q.")


@dp.message(F.text == "👤 Profilim")
async def show_profile(message: types.Message):
    data = await api.get_profile(message.from_user.id)
    if data:
        text = (f"👤 <b>Sizning profilingiz:</b>\n\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n"
                f"👤 Ism: {data.get('username', 'Noma\'lum')}\n"
                f"📞 Tel: {data.get('phone_number', 'Kiritilmagan')}\n"
                f"📍 Manzil: {data.get('address', 'Kiritilmagan')}")
        await message.answer(text)
    else:
        await message.answer("❌ Profilingiz topilmadi. Buyurtma berganingizda ma'lumotlar avtomatik saqlanadi.")


@dp.message(F.text == "📦 Buyurtmalarim")
async def show_orders(message: types.Message):
    orders = await api.get_orders(message.from_user.id)
    if orders:
        text = "📦 <b>Oxirgi buyurtmalaringiz:</b>\n\n"
        for o in orders:
            status = "✅" if o['status'] == 'delivered' else "⏳"
            text += f"🆔 #{o['id']} | {status} {o['status']}\n💰 Summa: {o['total_amount']} $\n\n"
        await message.answer(text)
    else:
        await message.answer("📭 Sizda hali buyurtmalar mavjud emas.")


@dp.message(F.text == "ℹ️ Ma'lumot")
async def show_info(message: types.Message):
    info_text = (
        "🏢 <b>Iron Shop - Temir Darvozalar Markazi</b>\n\n"
        "Bizning darvozalarimiz:\n"
        "✅ Yuqori sifatli metalldan\n"
        "✅ Zamonaviy dizaynda\n"
        "✅ Hamyonbop narxlarda tayyorlanadi."
    )
    await message.answer(info_text)


@dp.message(F.text == "📞 Bog'lanish")
async def contact_admin(message: types.Message):
    contact_text = (
        "📞 <b>Biz bilan bog'lanish:</b>\n\n"
        "📱 Telefon: +998 90 857 18 11\n"
        "👨‍💻 Admin: @darvozaadmin\n"
        "📍 Manzil: Farg'ona viloyati"
    )
    await message.answer(contact_text)


@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    cat_id = callback.data.split("_")[1]
    products = await api.get_products_by_category(cat_id)

    if not products:
        await callback.message.answer("❌ Mahsulotlar topilmadi.")
    else:
        for p in products:
            caption = f"🏷 <b>{p['name']}</b>\n💰 Narxi: {p['price']} $\n\n{p.get('description', '')}"
            img = p.get('image')
            if img and not img.startswith('http'):
                img = f"{DJANGO_HOST.rstrip('/')}{img}"

            try:
                if img:
                    await callback.message.answer_photo(photo=img, caption=caption,
                                                        reply_markup=kb.buy_product_kb(p['id']))
                else:
                    await callback.message.answer(caption, reply_markup=kb.buy_product_kb(p['id']))
            except Exception:
                await callback.message.answer(caption, reply_markup=kb.buy_product_kb(p['id']))
    await callback.answer()


# --- ASOSIY ISHGA TUSHIRISH ---

async def main():
    # Web serverni orqa fonda ishga tushirish
    asyncio.create_task(start_web_server())
    logging.info("🚀 Bot polling rejimida ishlamoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")