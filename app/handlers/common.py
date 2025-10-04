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

import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.keyboards as kb
from config import ADMIN_ID, bot
from app.services.logger import log_user_action, log_admin_action, log_error

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    try:
        if message.from_user.id in ADMIN_ID:
            log_admin_action(message.from_user.id, "Started bot")
            await rq.set_user(message.from_user.id)
            await message.answer(
                "О, ку! 👋\nНа менюшку, може вона тобі треба 😊",
                reply_markup=kb.admin_main,
            )
        else:
            log_user_action(
                message.from_user.id, message.from_user.username, "Started bot"
            )
            for admin in ADMIN_ID:
                await bot.send_message(
                    chat_id=admin,
                    text=f"Зареєстровано нового користувача: {message.from_user.full_name}\nLink: tg://user?id={message.from_user.id}:",
                )

            await rq.set_user(message.from_user.id)
            await message.answer(
                """👋 Вітаю в AbitAssistant_Bot!

Цей бот допоможе абітурієнтам (тобто майбутнім студентам 😋) швидко та зручно відфільтрувати своїх конкурентів, щоб не витрачати час на рутинну роботу, яку легко автоматизувати.

📌 Програма буде особливо корисною для тих, хто тільки подає заявки до університетів!

P.S. Якщо у вас 200 хоча б з одного, або з усіх предметів НМТ — не хвилюйтесь. Для вас конкуренції просто не існує 🫣

😉 Успіхів вам і легкого вступу! ✊"""
            )

            await message.answer(
                "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче 👇",
                reply_markup=kb.user_main,
            )
    except Exception as e:
        log_error(e, f"Error in start command for user {message.from_user.id}")


@router.message(F.text == "❌ До головного меню")
async def return_back(message: Message, state: FSMContext):
    try:
        if message.from_user.id in ADMIN_ID:
            await state.set_state(None)
            await message.answer(
                "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче 👇",
                reply_markup=kb.admin_main,
            )
        else:
            await state.set_state(None)
            await message.answer(
                "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче 👇",
                reply_markup=kb.user_main,
            )
    except Exception as e:
        log_error(e, f"Error in return_back for user {message.from_user.id}")


@router.message(F.text == "💸 Донат 💸")
async def donate(message: Message):
    try:
        await message.answer(
            """Сюди ви можете задонатити мені на новий ноутбук для навчання та програмування, буду дуже вдячний 🥰

🎯 Ціль: 70 000 ₴

🔗 Посилання на банку
https://send.monobank.ua/jar/23E3WYNesG

💳 Номер картки банки
5375 4112 0596 9640
                                        """,
            reply_markup=kb.return_back,
        )
    except Exception as e:
        log_error(e, f"Error in donate command for user {message.from_user.id}")


@router.message(F.text == "📑 Про нас 📑")
async def about_us(message: Message):
    try:
        await message.answer(
            "Захотілося почитати історію проєкту? 😊", reply_markup=kb.remove_keyboard
        )
        await asyncio.sleep(2)
        await message.answer("Тоді тримай 😊")
        await message.answer(
            """👋 Вітаю! Я — першокурсник Фахового коледжу інформаційних технологій НУ "Львівська Політехніка".

Цей бот — мій pet-project і водночас корисний проєкт для багатьох. Не судіть суворо — усе зроблено самостійно та з душею 😊

🎯 Мета проєкту:
    1. Отримати досвід у Python, парсингу, роботі з базами даних та Telegram API.
    2. Допомогти вступникам швидко й зручно подати документи з більшими шансами на бюджет, без зайвої метушні та ручного фільтрування."""
        )

        await message.answer(
            """📖 Трішки історії:

Усе почалося ще в 2024 році, коли я вступав у коледж, а мій товариш — в університет. Щоб допомогти йому з подачею документів я написав скрипт на основі відео TurboZNO, який працював із .txt-файлом і в консолі.
Пізніше ми зробили графічний інтерфейс через Tkinter, але програма залишалась локальною: потрібен був ПК, Python, ручне копіювання даних з сайту...

💡 Так з'явилась ідея створити телеграм-бота.

👀 Відео, на основі якого був створений бот:
https://www.youtube.com/watch?v=m5YfI8_2ONo

👨‍💻 Стара версія з Tkinter:
https://github.com/OlexiyOdarchuk/Competition-Check"""
        )

        await message.answer(
            """🤖 Telegram-версія — зручніша та доступна кожному:

🔧 Бот використовує:
    - Браузерні драйвери (Selenium),
    - Бази даних PostgreSQL,
    - Парсери та асинхронний код.

🧑‍💻 Весь код — у відкритому доступі, під ліцензією GPLv3:
https://github.com/OlexiyOdarchuk/AbitAssistant_bot"""
        )

        await message.answer(
            """🙏 Якщо вам сподобалась ідея або бот був корисним, підтримайте проєкт донатом — навіть кілька гривень важливі для покриття витрат на сервери.

🛠 А ще — долучайтесь до розробки або лишайте свої пропозиції на GitHub та в 'Зв'язок з адміністрацією' 👨‍💻""",
            reply_markup=kb.about_us,
        )
    except Exception as e:
        log_error(e, f"Error in about_us command for user {message.from_user.id}")
