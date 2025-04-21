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
from config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id in ADMIN_ID:
        await rq.set_user(message.from_user.id)
        await message.answer(
            "О, ку!\nНа менюшку, може вона тобі треба)", reply_markup=kb.admin_main
        )
    else:
        await rq.set_user(message.from_user.id)
        await message.answer("""Вітаю в боті для перевірки конкурекції! 👋

Тут ми реалізували фільтрацію конкурентів для абітурієнтів(тобто майбуніх студентів😋),
щоб ви не витрачали свій дорогоцінний час на однотипну роботу, яка, як правило, добре автоматизується!
Ця програма буде корисна для тих,
хто тільки подає заявки до університетів!

P.s. Та має не 200 з усіх предметів НМТ..
Для вас взагалі конкуренції не існує🫣

                            😉Успіхів!✊
""")
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main,
        )

@router.message(F.text == "❌ До головного меню")
async def return_back(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await state.set_state(None)
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.admin_main,
        )
    else:
        await state.set_state(None)
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main,
        )


@router.message(F.text == "💸Донат💸")
async def donate(message: Message):
    await message.answer(
        """Сюди ви можете задонатити мені на новий ноутбук для навчання та програмування, буду дуже вдячний 🥰

🎯 Ціль: 70 000 ₴

🔗Посилання на банку
https://send.monobank.ua/jar/23E3WYNesG

💳Номер картки банки
5375 4112 0596 9640
                                        """,
        reply_markup=kb.return_back,
    )


@router.message(F.text == "📑Про нас📑")
async def about_us(message: Message):
    await message.answer(
        "Хтось взагалі натискає на цю кнопку?...", reply_markup=kb.remove_keyboard
    )
    await asyncio.sleep(2)
    await message.answer("Ну раз натиснули, значить цікаво)))")
    await asyncio.sleep(1)
    await message.answer(
        "Тут тіпа шось написав щось дуже важне прям огого тут я допишу коли-небудь шось про себе і взагалі цю програму, бо щас лєнь придумувати.\
\nВзагалі я бідний студент, так що давайте якось задонатьте, чи що ",
        reply_markup=kb.about_us,
    )
