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
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.services.applicants_len as applicantlen
from app.states import States as st
from collections import defaultdict

user_score = defaultdict(dict)
router = Router()

@router.message(F.text == "📝Почати відсіювання!📝")
async def start_filter(message: Message, state: FSMContext):
    await message.answer("Введіть свій коефіцієнтний бал на вибрану для фільтрації спеціальність в форматі '123.456'\n\
\n\nПодивитися коефіцієнти можна на сайті https://www.education.ua/vstup/weighting-coefficients/\
\n\nА порахувати коефіцієнтний бал на сайті: https://osvita.ua/consultations/konkurs-ball/", reply_markup=kb.return_back)
    await state.set_state(st.get_bal)

@router.message(st.get_bal, F.text)
async def get_bal(message: Message, state: FSMContext):
    try:
        if 100.000 <= float(message.text) <= 200.000:
            user_score[message.from_user.id]['score'] = message.text
            await state.set_state(st.get_link)
            await message.answer("Супер! Тепер відправте посилання на освітню програму з сайту vstup.osvita, наприклад:\n'https://vstup.osvita.ua/y2024/r27/41/1352329/'")
        else:
            await message.answer('Ваш бал повинен бути в межах від 100 до 200')
    except ValueError:
        await message.answer("Будь ласка, введіть число в межах від 100 до 200")

@router.message(st.get_link, F.text)
async def get_link(message: Message, state: FSMContext):
    try:
        if message.text.startswith('https://vstup.osvita.ua'):
            await state.set_state(st.choice_list)
            # await fltr.filter_applicants(message.from_user.id, user_score) # Це буде тоді, коли допишу фільтр
            await message.answer("Сканування почалося. Це займе деякий час", reply_markup=kb.remove_keyboard)
            await asyncio.sleep(3)
            await message.answer("Зачекайте ще декілька секунд...")
            await asyncio.sleep(7)
            await message.answer("Ще трохи...")
            await asyncio.sleep(7)
            await message.answer("Майже готово...")
            await asyncio.sleep(7)
            await message.answer("Останні штрихи...")
            await asyncio.sleep(3)
            await message.answer("Готово!", reply_markup=kb.return_back)
            how_all_applicant = await applicantlen.all_applicant_len(message.from_user.id)
            how_competitor_applicant = await applicantlen.competitors_applicant_len(message.from_user.id)
            await message.answer(f"На цю освітню програму наразі подано {how_all_applicant}, але з усіх цих людей конкуренцію вам складають тільки {how_competitor_applicant}\
\nМожете дізнатися більше, використовуючи кнопки нище, або поверніться до головного меню, щоб перевірити інші освітні програми!", reply_markup=kb.applicant_stat)


        else:
            await message.answer("Посилання повинно починатися з 'https://vstup.osvita.ua' та бути коректним")
    except ValueError:
        await message.answer("Будь ласка, введіть посилання на освітню програму")
