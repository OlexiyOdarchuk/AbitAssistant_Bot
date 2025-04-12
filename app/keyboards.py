from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
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

async def builder_abit_all(tg_id:int, page:int) -> InlineKeyboardMarkup:
    abits = InlineKeyboardBuilder()
    data = await rq.get_user_data(tg_id)

    user_abits = [abit for abit in data if abit.user_tg_id == tg_id] # абітурієнт додається, тільки якщо він є в базі даних конкретного користувача

    per_page = 10
    total_pages = (len(user_abits) + per_page - 1) // per_page
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    current_page_abits = user_abits[start:end]

    for abits_all in current_page_abits:
        abit_name = " ".join(abits_all.name.split(" ")[:2])
        abits.button(
                text=f"                    Ім'я: '{abit_name}' Бал: {abits_all.score}                    ", #Я тут тупо не знайшов інших способів зробити нормальний вигляд
                callback_data=f'abit_{abits_all.id}'
            )
    abits.adjust(1)

    nav_buttons = InlineKeyboardBuilder()
    #Тут щас буде та сама фігня з відступами. Ну немає в мене ідей і всьо, тільки якщо такими костилями
    if page > 1: # Це умова, щоб додавати кнопку "◀️", тільки якщо є попередня сторінка
        nav_buttons.button(text="◀️", callback_data=f"abit_page_{page-1}")
    nav_buttons.button(text=f"{page}/{total_pages}", callback_data="abit_back_to_stat")
    if page < total_pages:# Це умова, щоб додавати кнопку "▶️", тільки якщо є наступна сторінка
        nav_buttons.button(text="▶️", callback_data=f"abit_page_{page+1}")
    nav_buttons.adjust(3)# Це, щоб вони були в одному рядку

    abits.attach(nav_buttons)

    return abits.as_markup()

async def builder_abit_competitions(tg_id:int, user_score:float, page:int) -> InlineKeyboardMarkup:
    abits = InlineKeyboardBuilder()
    data = await rq.get_user_data(tg_id)

    user_competitors = [abit for abit in data if abit.user_tg_id == tg_id and abit.competitor] # Конкурент додається, тільки якщо він є у базі данних конкретного користувача

    per_page = 10
    total_pages = (len(user_competitors) + per_page - 1) // per_page # Вираховує поточну кількість сторінок
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    current_page_competitors = user_competitors[start:end]

    for competitors_all in current_page_competitors:
        competitor_name = " ".join(competitors_all.name.split(" ")[:2])
        abits.button(
                text=f"Ім'я: '{competitor_name}' Бал: {competitors_all.score}",
                callback_data=f'competitors_{competitors_all.id}'
            )
        abits.adjust(1)

    nav_buttons = InlineKeyboardBuilder()
    #Тут щас буде та сама фігня з відступами. Ну немає в мене ідей і всьо, тільки якщо такими костилями
    if page > 1: # Це умова, щоб додавати кнопку "◀️", тільки якщо є попередня сторінка
        nav_buttons.button(text="        ◀️        ", callback_data=f"competitors_page_{page-1}")
    nav_buttons.button(text=f"        {page}/{total_pages}        ", callback_data="abit_back_to_stat")
    if page < total_pages: # Це умова, щоб додавати кнопку "▶️", тільки якщо є наступна сторінка
        nav_buttons.button(text="        ▶️        ", callback_data=f"competitors_page_{page+1}")
    nav_buttons.adjust(3)

    abits.attach(nav_buttons)

    return abits.as_markup()


abit_stat = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Всі абітурієнти', callback_data="view_abit_all"), InlineKeyboardButton(text="Тільки конкуренти", callback_data="view_abit_competitors")]
    ]
)
