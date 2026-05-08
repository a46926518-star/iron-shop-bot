import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

import api_service as api
import keyboards as kb
from config import BOT_TOKEN, DJANGO_HOST
from aiogram.filters import Command


class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def start_command(message: types.Message):
    categories = await api.get_categories()

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        "Kategoriyalardan birini tanlang:",
        reply_markup=kb.categories_kb(categories)
    )


@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    cat_id = callback.data.split("_")[1]
    products = await api.get_products_by_category(cat_id)

    if not products:
        await callback.message.answer("❌ Bu kategoriyada mahsulotlar topilmadi.")
    else:
        for p in products:
            caption = f"🏷 <b>{p['name']}</b>\n💰 Narxi: {p['price']} $\n\n{p.get('description', '')}"
            img = p.get('image')

            if img and not img.startswith('http'):
                img = f"{DJANGO_HOST.rstrip('/')}{img}"

            markup = kb.buy_product_kb(p['id'])

            try:
                if img:
                    await callback.message.answer_photo(photo=img, caption=caption, reply_markup=markup)
                else:
                    await callback.message.answer(caption, reply_markup=markup)
            except Exception as e:
                logging.error(f"Rasm yuborishda xato: {e}")
                await callback.message.answer(caption, reply_markup=markup)

    await callback.answer()


@dp.callback_query(F.data.startswith("buy_"))
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]
    await state.update_data(selected_product_id=product_id)

    await callback.answer("Buyurtma boshlandi")
    await callback.message.answer("📝 Buyurtmani rasmiylashtirish uchun to'liq ismingizni kiriting:")
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer(f"Rahmat, {message.text}! Endi telefon raqamingizni yuboring:",
                         reply_markup=kb.contact_markup())
    await state.set_state(OrderState.waiting_for_phone)


@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text



    await message.answer(
        "✅ **Rahmat! Buyurtmangiz qabul qilindi.**\n"
        "Tez orada mutaxassislarimiz siz bilan bog'lanishadi.",
        reply_markup=kb.main_menu
    )

    await state.clear()