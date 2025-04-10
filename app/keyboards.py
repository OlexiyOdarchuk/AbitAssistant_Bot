from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import app.database.requests as rq
remove_keyboard = ReplyKeyboardRemove()

admin_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝Почати відсіювання!📝")],
        [KeyboardButton(text="💸Донат💸"), KeyboardButton(text="📑Про нас📑")],
        [KeyboardButton(text="📣Розсилка!")],
    ],
    resize_keyboard=True,
)

user_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝Почати відсіювання!📝")],
        [KeyboardButton(text="💸Донат💸"), KeyboardButton(text="📑Про нас📑")],
        [KeyboardButton(text="👤Зв'язок з адміністрацією👤")],
    ],
    resize_keyboard=True,
)

support = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ До головного меню"), KeyboardButton(text="📤 Відправити"),
        ],
    ],
    resize_keyboard=True,
)

return_back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ До головного меню")]], resize_keyboard=True
)

about_us = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💸Донат💸"), KeyboardButton(text="❌ До головного меню")
        ],
    ],
    resize_keyboard=True,
)

mailing = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Відправити розсилку📣"), KeyboardButton(text="❌ До головного меню"),
        ],
    ],
    resize_keyboard=True,
)

# async def generate_category_buttons(tg_id):
#     data = rq.get_all_user_data(tg_id)
#     abiturients = InlineKeyboardMarkup()

#     for cat_id, cat_nam in data:
#         abiturients.add(
#             InlineKeyboardButton(text=cat_name, callback_data=f"category_{cat_id}")
#         )

#     return abiturients
