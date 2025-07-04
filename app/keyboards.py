# Copyright (c) 2025 iShawyha. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        [KeyboardButton(text="🧠 Розпочати аналіз та фільтрацію 📊")],
        [KeyboardButton(text="💸 Донат 💸"), KeyboardButton(text="📑 Про нас 📑")],
        [KeyboardButton(text="📣 Розсилка"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Користувачі"), KeyboardButton(text="📋 Логи")],
    ],
    resize_keyboard=True,
)

user_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Розпочати аналіз та фільтрацію 📊")],
        [KeyboardButton(text="💸 Донат 💸"), KeyboardButton(text="📑 Про нас 📑")],
        [KeyboardButton(text="👤 Зв'язок з адміністрацією 👤")],
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
            KeyboardButton(text="💸 Донат 💸"), KeyboardButton(text="❌ До головного меню")
        ],
    ],
    resize_keyboard=True,
)

mailing = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📣 Відправити розсилку"), KeyboardButton(text="❌ До головного меню"),
        ],
    ],
    resize_keyboard=True,
)

async def builder_applicant_all(tg_id:int, page:int) -> InlineKeyboardMarkup:
    applicants = InlineKeyboardBuilder()
    data = await rq.get_user_data(tg_id)

    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id] # абітурієнт додається, тільки якщо він є в базі даних конкретного користувача

    per_page = 10
    total_pages = (len(user_applicants) + per_page - 1) // per_page
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    current_page_applicants = user_applicants[start:end]

    for applicants_all in current_page_applicants:
        applicant_name = " ".join(applicants_all.name.split(" ")[:2])
        applicants.button(
                text=f"        👤 {competitor_name} | Бал: {competitors_all.score}        ",
                callback_data=f'applicant_{applicants_all.id}'
            )
    applicants.adjust(1)

    nav_buttons = InlineKeyboardBuilder()
    #Тут щас буде фігня з відступами. Ну немає в мене ідей і всьо, тільки якщо такими костилями
    if page > 1: # Це умова, щоб додавати кнопку "◀️", тільки якщо є попередня сторінка
        nav_buttons.button(text="        ◀️        ", callback_data=f"applicant_page_{page-1}")
    nav_buttons.button(text=f"        {page}/{total_pages}        ", callback_data="applicant_back_to_stat")
    if page < total_pages:# Це умова, щоб додавати кнопку "▶️", тільки якщо є наступна сторінка
        nav_buttons.button(text="        ▶️        ", callback_data=f"applicant_page_{page+1}")
    nav_buttons.adjust(3)# Це, щоб вони були в одному рядку

    applicants.attach(nav_buttons)

    return applicants.as_markup()

async def builder_applicant_competitors(tg_id:int, user_score:float, page:int) -> InlineKeyboardMarkup:
    applicants = InlineKeyboardBuilder()
    data = await rq.get_user_data(tg_id)

    user_competitors = [applicant for applicant in data if applicant.user_tg_id == tg_id and applicant.competitor] # Конкурент додається, тільки якщо він є у базі данних конкретного користувача

    per_page = 10
    total_pages = (len(user_competitors) + per_page - 1) // per_page # Вираховує поточну кількість сторінок
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    current_page_competitors = user_competitors[start:end]

    for competitors_all in current_page_competitors:
        competitor_name = " ".join(competitors_all.name.split(" ")[:2])
        applicants.button(
                text=f"        👤 {competitor_name} | Бал: {competitors_all.score}        ",
                callback_data=f'applicant_{competitors_all.id}'
            )
        applicants.adjust(1)

    nav_buttons = InlineKeyboardBuilder()
    #Тут щас буде та сама фігня з відступами. Ну немає в мене ідей і всьо, тільки якщо такими костилями
    if page > 1: # Це умова, щоб додавати кнопку "◀️", тільки якщо є попередня сторінка
        nav_buttons.button(text="        ◀️        ", callback_data=f"competitors_page_{page-1}")
    nav_buttons.button(text=f"        {page}/{total_pages}        ", callback_data="applicant_back_to_stat")
    if page < total_pages: # Це умова, щоб додавати кнопку "▶️", тільки якщо є наступна сторінка
        nav_buttons.button(text="        ▶️        ", callback_data=f"competitors_page_{page+1}")
    nav_buttons.adjust(3)

    applicants.attach(nav_buttons)

    return applicants.as_markup()


applicant_stat = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📋 Всі абітурієнти', callback_data="view_applicant_all"), InlineKeyboardButton(text="🎯 Тільки конкуренти", callback_data="view_applicant_competitors")]
    ]
)
