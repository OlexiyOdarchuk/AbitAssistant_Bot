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

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.services.parse_in_db import parser
import app.keyboards as kb
import app.services.stats as stats
from app.states import States as st
from config import MULTITASK

router = Router()


@router.message(F.text == "📝Почати відсіювання!📝")
async def start_filter(message: Message, state: FSMContext):
    await message.answer("Введіть свій коефіцієнтний бал для цієї спеціальності у форматі 123.456.\n\
\n\n🔗 Подивитися коефіцієнти: https://www.education.ua/vstup/weighting-coefficients/\
\n\n🧮 Порахувати бал: https://osvita.ua/consultations/konkurs-ball/", reply_markup=kb.return_back)
    await state.set_state(st.get_bal)

@router.message(st.get_bal, F.text)
async def get_bal(message: Message, state: FSMContext):
    try:
        score = float(message.text.replace(',', '.'))
        if 100.000 <= score <= 200.000:
            stats.user_score[message.from_user.id] = score
            await state.set_state(st.get_link)
            await message.answer(
                "Чудово! 🎯\n\n"
                "Тепер надішліть посилання на сторінку освітньої програми з сайту vstup.osvita.ua.\n\n"
                "Наприклад:\n"
                "https://vstup.osvita.ua/y2025/r27/41/1352329/\n\n"
                "🔗 Переконайтесь, що посилання починається з 'https://vstup.osvita.ua/y2025/'"
            )
        else:
            await message.answer("❗ Ваш бал має бути в межах від 100 до 200.")
    except ValueError:
        await message.answer("⚠️ Будь ласка, введіть дійсне число в межах від 100 до 200.")

@router.message(st.get_link, F.text)
async def get_link(message: Message, state: FSMContext):
    try:
        if message.text.startswith('https://vstup.osvita.ua'): #НЕ ЗАБУДЬ СЮДИ ВПИСАТИ y2025!!!!
            await state.set_state(st.choice_list)
            await message.answer(
                "🔍 Сканування розпочато. Це займе до 3 хвилин...\n\nP.S. Усе одно швидше, ніж вручну 😄",
                reply_markup=kb.remove_keyboard
            )

            # Очікуємо, доки звільниться місце у семафорі
            async with MULTITASK:
                try:
                    await parser(message.text, message.from_user.id)
                except Exception:
                    await message.answer(
                        "Упс.. надто багато обробок, система не витримує, спробуйте ще раз 🙂",
                        reply_markup=kb.user_main
                    )
                    return

            await message.answer("Готово!", reply_markup=kb.return_back)
            how_all_applicant = await stats.all_applicant_len(message.from_user.id)
            how_competitor_applicant = await stats.competitors_applicant_len(message.from_user.id)
            await message.answer(
                f"""🔍 Аналіз завершено!
На цю освітню програму наразі подано {how_all_applicant} бюджетних заявок.
Але лише {how_competitor_applicant} з них — це ваші справжні конкуренти 😉

📊 Використовуйте кнопки нижче, щоб дізнатись більше, або повертайтесь у головне меню для нової перевірки!
            """,
                reply_markup=kb.applicant_stat
            )


        else:
            await message.answer("Посилання повинно починатися з 'https://vstup.osvita.ua/y2025/' та бути коректним")
    except ValueError:
        await message.answer("Будь ласка, введіть посилання на освітню програму")
