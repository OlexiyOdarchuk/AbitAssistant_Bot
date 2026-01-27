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
from urllib.parse import urlparse

# from app.services.parse_in_db_OLD import parser
from app.services.logger import (
    log_user_action,
    log_admin_action,
    log_error,
    log_system_event,
)
import app.keyboards as kb
import app.services.stats as stats
from app.states import States as st
from config import MULTITASK, ADMIN_ID

router = Router()


@router.message(F.text == "🧠 Розпочати аналіз та фільтрацію 📊")
async def start_filter(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        if user_id in ADMIN_ID:
            log_admin_action(user_id, "Started analysis and filtering")
        else:
            log_user_action(user_id, username, "Started analysis and filtering")

        await message.answer(
            "Перед початком роботи, будь ласка, перегляньте це відео для розуміння того, як працювати з отриманими даними: https://www.youtube.com/watch?v=m5YfI8_2ONo",
            reply_markup=kb.remove_keyboard,
        )
        await message.answer(
            "Введіть свій коефіцієнтний бал для цієї спеціальності у форматі 123.456.\n\n🔗 Подивитися коефіцієнти: https://www.education.ua/vstup/weighting-coefficients/\n\n🧮 \n\n Порахувати бал: https://osvita.ua/consultations/konkurs-ball/",
            reply_markup=kb.return_back,
        )
        await state.set_state(st.get_bal)
    except Exception as e:
        log_error(e, f"Error in start_filter for user {message.from_user.id}")


@router.message(st.get_bal, F.text)
async def get_bal(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        score_text = message.text

        log_user_action(user_id, username, "Entered score", f"Score: {score_text}")

        score = float(score_text.replace(",", "."))
        if 100.000 <= score <= 200.000:
            stats.user_score[user_id] = score
            log_user_action(
                user_id, username, "Score validated", f"Valid score: {score}"
            )

            await state.set_state(st.get_link)
            await message.answer(
                "Чудово! 🎯\n\n"
                "Тепер надішліть посилання на сторінку освітньої програми з сайту vstup.osvita.ua.\n\n"
                "Наприклад:\n"
                "https://vstup.osvita.ua/y2025/r27/41/1352329/\n\n"
                "🔗 Переконайтесь, що посилання починається з 'https://vstup.osvita.ua/y2025/'"
            )
        else:
            log_user_action(
                user_id,
                username,
                "Invalid score entered",
                f"Score out of range: {score}",
            )
            await message.answer("❗ Ваш бал має бути в межах від 100 до 200.")
    except ValueError:
        user_id = message.from_user.id
        username = message.from_user.username
        log_user_action(
            user_id,
            username,
            "Invalid score format",
            f"Non-numeric score: {message.text}",
        )
        await message.answer(
            "⚠️ Будь ласка, введіть дійсне число в межах від 100 до 200."
        )
    except Exception as e:
        log_error(e, f"Error in get_bal for user {message.from_user.id}")


@router.message(st.get_link, F.text)
async def get_link(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        url = message.text

        log_user_action(user_id, username, "Entered URL", f"URL: {url}")

        parsed_url = urlparse(message.text)
        if (
            parsed_url.hostname == "vstup.osvita.ua"
        ):  #! НЕ ЗАБУДЬ СЮДИ ВПИСАТИ y2026!!!!
            if "@" not in message.text:
                log_user_action(
                    user_id, username, "URL validated", "Starting parsing process"
                )

                await state.set_state(st.choice_list)
                await message.answer(
                    "🔍 Сканування розпочато. Це займе до 3 хвилин...\n\nP.S. Усе одно швидше, ніж вручну 😄",
                    reply_markup=kb.remove_keyboard,
                )
            else:
                log_user_action(
                    user_id,
                    username,
                    "Suspicious URL detected",
                    f"URL contains @: {url}",
                )
                await message.answer(
                    "❗ Ах ти хакер, блін, своїми фейковими посиланнями тут не розкидуйся ❗",
                    reply_markup=kb.user_main,
                )
                return

            # Жде чергу
            async with MULTITASK:
                try:
                    log_system_event(
                        "Parsing started", f"User {user_id} started parsing URL: {url}"
                    )

                    """
                    if await parser(url, user_id) == "Error":
                        log_user_action(
                            user_id,
                            username,
                            "Parsing failed",
                            f"Error returned for URL: {url}",
                        )
                        await message.answer(
                            "🧮 Помилка при обробці даних, перевірте ваше посилання, можливо воно хибне 🙂",
                            reply_markup=kb.user_main,
                        )
                        return
                    """

                    #! ОБОВ'ЯЗКОВО ЦЕ ПОВЕРНУТИ

                    await message.answer(
                        "🧮 Зараз використовується версія, яка не парсить дані. Це версія підготовки до переходу на нову технологію парсингу, тому результату тут немає 🙂",
                        reply_markup=kb.user_main,
                    )
                    return

                except Exception as e:
                    log_error(e, f"Parsing exception for user {user_id}, URL: {url}")
                    await message.answer(
                        "Упс... у нас внутрішня помилка, спробуйте ще раз 🙂",
                        reply_markup=kb.user_main,
                    )
                    return

            log_user_action(
                user_id, username, "Parsing completed successfully", f"URL: {url}"
            )
            await message.answer("Готово! ✅", reply_markup=kb.return_back)

            how_all_applicant = await stats.all_applicant_len(user_id)
            how_competitor_applicant = await stats.competitors_applicant_len(user_id)

            log_user_action(
                user_id,
                username,
                "Analysis results",
                f"Total applicants: {how_all_applicant}, Competitors: {how_competitor_applicant}",
            )

            await message.answer(
                f"""🔍 Аналіз завершено!\nНа цій освітній програмі наразі активно {how_all_applicant} бюджетних заявок.\nАле лише {how_competitor_applicant} з них — це ваші справжні конкуренти 😉\n\n📊 Використовуйте кнопки нижче, щоб дізнатись більше, або повертайтесь у головне меню для нової перевірки!\n            """,
                reply_markup=kb.applicant_stat,
            )

        else:
            log_user_action(
                user_id,
                username,
                "Invalid URL format",
                f"URL doesn't start with vstup.osvita.ua: {url}",
            )
            await message.answer(
                "Посилання повинно починатися з 'https://vstup.osvita.ua/y2025/' та бути коректним"
            )
    except ValueError:
        user_id = message.from_user.id
        username = message.from_user.username
        log_user_action(
            user_id,
            username,
            "URL validation error",
            f"ValueError for URL: {message.text}",
        )
        await message.answer("Будь ласка, введіть посилання на освітню програму")
    except Exception as e:
        log_error(e, f"Error in get_link for user {message.from_user.id}")