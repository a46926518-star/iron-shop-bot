import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

import keyboards as kb
from api_service import api
from config import BOT_TOKEN, DJANGO_HOST

logging.basicConfig(level=logging.INFO)


class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    categories = await api.get_categories()
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n"
        "Iron Shop botiga xush kelibsiz. Kategoriyani tanlang:",
        reply_markup=kb.categories_kb(categories)
    )

    await message.answer("Menyu:", reply_markup=kb.main_menu)


@dp.message(F.text == "🚪 Katalog")
async def show_katalog(message: types.Message):
    categories = await api.get_categories()
    await message.answer("Kategoriyani tanlang:", reply_markup=kb.categories_kb(categories))


@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    cat_id = callback.data.split("_")[1]
    products = await api.get_products_by_category(cat_id)

    if not products:
        await callback.answer("❌ Mahsulotlar yo'q", show_alert=True)
        return

    for p in products:
        caption = f"<b>{p['name']}</b>\n\n💰 Narxi: {p['price']} $\n📝 {p.get('description', '')}"
        img = p.get('image')

        if img and not img.startswith('http'):
            img = f"{DJANGO_HOST}{img}"

        markup = kb.buy_product_kb(p['id'])

        if img:
            await callback.message.answer_photo(photo=img, caption=caption, reply_markup=markup)
        else:
            await callback.message.answer(caption, reply_markup=markup)

    await callback.answer()

    @dp.callback_query(F.data.startswith("category:"))
    async def show_products(callback: types.CallbackQuery):
        cat_id = callback.data.split(":")[1]
    await state.update_data(product_id=p_id)

    await callback.message.answer("📝 Ismingizni kiriting:")
    await state.set_state(OrderState.waiting_for_name)
    await callback.answer()


@dp.message(OrderState.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Rahmat, {message.text}! Endi raqamingizni yuboring:",
                         reply_markup=kb.contact_markup())
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()

    phone = message.contact.phone_number if message.contact else message.text

    order_data = {
        "product_id": data["product_id"],
        "name": data["name"],
        "phone": phone,
        "telegram_id": message.from_user.id
    }

    # 🔥 BACKENDGA YUBORISH (BU MUHIM)
    await api.create_order(order_data)

    await message.answer(
        "✅ Buyurtmangiz qabul qilindi!\nTez orada operator bog‘lanadi.",
        reply_markup=kb.main_menu
    )

    await state.clear()