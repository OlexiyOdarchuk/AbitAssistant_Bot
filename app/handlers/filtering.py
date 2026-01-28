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
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from urllib.parse import urlparse

from app.services.parser import parser
from app.services.decoder import decoder
from app.services.filter import filter_data
from app.services.results_cache import save_result, get_result
from app.services.visualization import generate_rating_histogram
from app.database.requests import get_user_nmt, update_user_activates, update_user_right_activates, save_specialty_list, get_cached_url, cache_url
from app.services.logger import (
    log_user_action,
    log_admin_action,
    log_error,
    log_system_event,
)
import app.keyboards as kb
from app.states import States as st
from app.states import ProfileStates as pst
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
            
        nmt_scores = await get_user_nmt(user_id)
        if not nmt_scores:
            await message.answer(
                "⛔️ **У вас не заповнені бали НМТ!**\n\n"
                "Без них я не можу порахувати ваш рейтинговий бал і визначити ваші шанси.\n"
                "Будь ласка, перейдіть в Налаштування профілю і додайте свої предмети.",
                parse_mode="Markdown"
            )
            return

        await message.answer(
            "Перед початком роботи, будь ласка, перегляньте це відео для розуміння того, як працювати з отриманими даними: https://www.youtube.com/watch?v=m5YfI8_2ONo",
            reply_markup=kb.remove_keyboard,
        )
        
        await message.answer(
            "Надішліть посилання на сторінку освітньої програми з сайту vstup.osvita.ua.\n\n"
            "Наприклад:\n"
            "https://vstup.osvita.ua/y2025/r27/41/1352329/\n\n"
            "🔗 Переконайтесь, що посилання починається з 'https://vstup.osvita.ua/y2025/'",
             reply_markup=kb.return_back
        )
        await state.set_state(st.get_link)
        
    except Exception as e:
        log_error(e, f"Error in start_filter for user {message.from_user.id}")


@router.message(st.get_link, F.text)
async def get_link(message: Message, state: FSMContext):
    await process_link(message, state, creative_score=0)


async def process_link(message: Message, state: FSMContext, creative_score: float = 0):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        url = message.text.strip()
        
        # Якщо це виклик з creative_score, url треба брати зі state
        if creative_score > 0:
            data = await state.get_data()
            url = data.get("current_url")
            decoded_data = data.get("decoded_data") # Вже розпарсені дані
        else:
            # Первинний виклик
            parsed_url = urlparse(url)
            if parsed_url.hostname != "vstup.osvita.ua":
                 await message.answer("Посилання повинно бути з домену vstup.osvita.ua")
                 return
            
            await state.update_data(current_url=url)
            
            # Check Global Cache first
            raw_data = await get_cached_url(url)
            
            if raw_data:
                await message.answer("⚡️ Дані знайдено в кеші! Аналіз буде миттєвим.")
                decoded_data = decoder(raw_data, user_id)
            else:
                status_msg = await message.answer(
                    "🔍 Сканування та аналіз розпочато...\n"
                    "Це може зайняти певний час, оскільки ми перевіряємо статус ваших конкурентів в реальному часі 🕵️‍♂️",
                    reply_markup=kb.remove_keyboard,
                )
                
                try:
                    async with MULTITASK:
                        raw_data = await parser(url, user_id)
                        if not raw_data or not raw_data.get("requests"):
                                await status_msg.delete()
                                await message.answer("❌ Не вдалося отримати дані з сайту або список порожній.")
                                return
                        
                        # Save to Global Cache
                        await cache_url(url, raw_data)
                        
                        decoded_data = decoder(raw_data, user_id)
                except Exception as e:
                    log_error(e, f"[User {user_id}] Error during parsing or decoding")
                    await status_msg.delete()
                    await message.answer("❌ Помилка при обробці даних...")
                    return
        
        # Перевірка на творчий конкурс
        subj_coeffs = decoded_data.get("subject_coefficients", {})
        if "Творчий конкурс" in subj_coeffs and creative_score == 0:
            await state.update_data(decoded_data=decoded_data) # Зберігаємо, щоб не парсити знову
            await message.answer(
                "🎨 **Увага! Ця спеціальність вимагає Творчий Конкурс.**\n"
                "Ваші бали НМТ тут мають меншу вагу (коефіцієнт творчого зазвичай вищий).\n\n"
                "Введіть ваш **орієнтовний бал** за творчий конкурс (100-200), щоб я міг порахувати шанси:",
                parse_mode="Markdown"
            )
            await state.set_state(pst.enter_creative_score)
            return

        # Filtering
        try:
            final_data = await filter_data(decoded_data, user_id, creative_contest_score=creative_score)
        except Exception as e:
            log_error(e, f"[User {user_id}] Error during filtering")
            await message.answer(
                "❌ Помилка при фільтрації конкурентів. Спробуйте ще раз."
            )
            return
            
        # Store URL in result for later reference
        final_data["url"] = url
        
        save_result(user_id, final_data)
        await update_user_activates(user_id)
        await update_user_right_activates(user_id)

        # Output
        analysis = final_data.get("analysis", {})
        chance = analysis.get("chance", "Unknown")
        advice = analysis.get("advice", "")
        my_rank = analysis.get("my_real_rank", "?")
        budget_spots = analysis.get("remaining_general", "?")
        user_rating = final_data.get("user_rating_score", 0)

        chance_emoji = {
            "High": "🟢 Високий",
            "High (Quota 1)": "🟢 Високий (Квота 1)",
            "High (Quota 2)": "🟢 Високий (Квота 2)",
            "Medium": "🟡 Середній",
            "Low": "🔴 Низький",
            "Zero": "⚫ Нульовий"
        }.get(chance, chance)
        
        # Async Graph Generation
        loop = asyncio.get_running_loop()
        title = f"Рейтинг: {final_data.get('university_name', '')[:20]}"
        
        # Run matplotlib in executor to avoid blocking
        try:
            photo = await loop.run_in_executor(
                None, 
                generate_rating_histogram, 
                final_data, 
                user_rating, 
                title
            )
        except Exception as e:
            log_error(e, f"[User {user_id}] Error generating histogram")
            photo = None

        caption = (
            f"📊 **Результати аналізу:**\n\n"
            f"🎯 **Ваш рейтинговий бал:** {user_rating:.3f}\n"
            f"🏆 **Ваше реальне місце:** {my_rank} (на {budget_spots} вільних місць)\n"
            f"🎲 **Шанс на вступ:** {chance_emoji}\n\n"
            f"💡 **Вердикт:** {advice}"
        )

        if photo:
            await message.answer_photo(
                photo,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=kb.applicant_stat,
            )
        else:
            await message.answer(
                caption,
                parse_mode="Markdown",
                reply_markup=kb.applicant_stat,
            )
            
        await state.set_state(st.choice_list) # Готові до перегляду списків

    except Exception as e:
        log_error(e, f"Error processing link for user {message.from_user.id}")
        await message.answer("Сталася неочікувана помилка. Будь ласка, спробуйте ще раз або напишіть адміністраторам.")


@router.message(pst.enter_creative_score)
async def enter_creative_score(message: Message, state: FSMContext):
    try:
        score = float(message.text.replace(",", "."))
        
        if 100 <= score <= 200:
            await message.answer(f"✅ Прийнято бал: {score}. Продовжую аналіз...")
            await process_link(message, state, creative_score=score)
        else:
            await message.answer("❌ Бал має бути від 100 до 200. Спробуйте ще раз:")
    except ValueError:
        await message.answer("❌ Введіть число (наприклад, 150.5):")
    except ValueError:
        await message.answer("Введіть число.")
