from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📂 Katalog")],
        [KeyboardButton(text="📦 Buyurtmalarim"), KeyboardButton(text="👤 Profilim")],
        [KeyboardButton(text="ℹ️ Ma'lumot"), KeyboardButton(text="📞 Bog'lanish")]
    ],
    resize_keyboard=True
)


def categories_kb(categories):
    builder = InlineKeyboardBuilder()

    for cat in categories:
        builder.button(
            text=f"📂 {cat.get('name')}",
            callback_data=f"category:{cat.get('id')}"
        )

    builder.adjust(2)
    return builder.as_markup()


def buy_product_kb(product_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Buyurtma berish", callback_data=f"buy:{product_id}")
    return builder.as_markup()


def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqam yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )