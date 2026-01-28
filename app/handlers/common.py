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
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.keyboards as kb
from config import ADMIN_ID, bot
from app.services.logger import log_user_action, log_admin_action, log_error
from app.services.results_cache import save_result
from app.services.visualization import generate_rating_histogram
from app.states import States as st
from app.states import ProfileStates as pst

router = Router()


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    
    user_id = message.from_user.id
    markup = kb.admin_main if user_id in ADMIN_ID else kb.user_main
    
    await message.answer("🚫 Дія скасована. Повернення до головного меню.", reply_markup=markup)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, command: CommandObject):
    try:
        user_id = message.from_user.id
        await rq.set_user(user_id)
        
        # --- Deep Linking (Sharing) ---
        args = command.args
        if args and args.startswith("list_"):
            try:
                list_id = int(args.replace("list_", ""))
                saved_list = await rq.get_saved_list(list_id)
                
                if saved_list:
                    await rq.save_specialty_list(
                        user_id, 
                        f"Копія: {saved_list.name}", 
                        saved_list.url, 
                        saved_list.data
                    )
                    
                    # Конвертуємо ключи зі str назад в int (JSON конвертує int ключі в str)
                    data = saved_list.data
                    requests = data.get("requests", {})
                    if requests:
                        competitors = requests.get("competitors", {})
                        non_competitors = requests.get("non-competitors", {})
                        
                        # Конвертуємо ключи зі str в int
                        data["requests"]["competitors"] = {int(k) if isinstance(k, str) and k.isdigit() else k: v for k, v in competitors.items()}
                        data["requests"]["non-competitors"] = {int(k) if isinstance(k, str) and k.isdigit() else k: v for k, v in non_competitors.items()}
                    
                    save_result(user_id, data)
                    
                    await message.answer(f"📥 Ви отримали спільний аналіз: **{saved_list.name}**\nВін збережений у вашому профілі.", parse_mode="Markdown")
                    
                    data = saved_list.data
                    analysis = data.get("analysis", {})
                    user_rating = data.get("user_rating_score", 0)
                    
                    try:
                        loop = asyncio.get_running_loop()
                        photo = await loop.run_in_executor(
                            None,
                            generate_rating_histogram,
                            data,
                            user_rating,
                            title=f"Рейтинг: {saved_list.name[:20]}"
                        )
                    except Exception as e:
                        log_error(e, "Error generating histogram in start")
                        photo = None
                    
                    caption = (
                        f"📊 **Результати аналізу:**\n\n"
                        f"🎯 **Рейтинговий бал:** {user_rating:.3f}\n"
                        f"🏆 **Місце:** {analysis.get('my_real_rank')} (з {analysis.get('total_budget')})\n"
                        f"🎲 **Шанс:** {analysis.get('chance')}\n\n"
                        f"Ви можете редагувати цей аналіз, переглядаючи список конкурентів."
                    )
                    
                    if photo:
                        await message.answer_photo(photo, caption=caption, parse_mode="Markdown", reply_markup=kb.applicant_stat)
                    else:
                        await message.answer(caption, parse_mode="Markdown", reply_markup=kb.applicant_stat)
                        
                    await state.set_state(st.choice_list)
                    return
                else:
                    await message.answer("⚠️ Посилання застаріло або список було видалено.")
            except ValueError as e:
                log_error(e, "Invalid list_id in deep link")
            except Exception as e:
                log_error(e, "Error processing deep link")

        # --- Standard Start ---
        if user_id in ADMIN_ID:
            log_admin_action(user_id, "Started bot")
            await message.answer("Адмін-панель активована.", reply_markup=kb.admin_main)
            return

        log_user_action(user_id, message.from_user.username, "Started bot")
        await message.answer(
            "👋 **Вітаю в AbitAssistant!**\n\n"
            "Я допоможу тобі оцінити реальні шанси на вступ, відсіявши тих, хто проходить на вищі пріоритети.\n"
            "Більше ніяких ручних підрахунків та Excel-таблиць! 🚀",
            parse_mode="Markdown",
            reply_markup=kb.user_main
        )
        
        nmt = await rq.get_user_nmt(user_id)
        if not nmt:
            await asyncio.sleep(1)
            await message.answer(
                "📝 **Давай заповнимо твій профіль!**\n\n"
                "Щоб я міг рахувати твій рейтинговий бал, мені потрібні твої результати НМТ.\n"
                "Це займе хвилину 👇",
                parse_mode="Markdown"
            )
            await message.answer("Обери перший предмет:", reply_markup=kb.get_subjects_kb({}))
            await state.set_state(pst.choose_subject)

    except Exception as e:
        log_error(e, f"Error in start command for user {message.from_user.id}")
        await message.answer("❌ Помилка при завантаженні. Спробуйте ще раз /start")


@router.message(F.text == "❌ До головного меню")
async def return_back(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        await state.clear()
        if user_id in ADMIN_ID:
            await message.answer("Головне меню", reply_markup=kb.admin_main)
        else:
            await message.answer("Головне меню", reply_markup=kb.user_main)
    except Exception as e:
        log_error(e, f"Error in return_back")


@router.message(F.text == "💸 Донат 💸")
async def donate(message: Message):
    await message.answer(
        "☕ **Підтримай розробку!**\n\n"
        "Цей бот існує завдяки ентузіазму та каві. Твій донат допоможе оплатити сервери та наблизить покупку ноутбука для розробки нових фіч.\n\n"
        "🎯 **Ціль:** Новий ноут для кодингу + підтримка серверів\n"
        "💳 **Банка:** [Monobank](https://send.monobank.ua/jar/23E3WYNesG)",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=kb.return_back
    )


@router.message(F.text == "📑 Про нас 📑")
async def about_us(message: Message):
    text = (
        "🤖 **AbitAssistant 2.0**\n\n"
        "Я — студент коледжу Львівської Політехніки, і я створив цей інструмент, бо сам пройшов через пекло вступу.\n\n"
        "**Що робить цей бот?**\n"
        "1. **Парсить** списки з vstup.osvita.ua.\n"
        "2. **Аналізує** конкурентів: перевіряє, чи проходять вони на вищі пріоритети (алгоритм \"The Technique\").\n"
        "3. **Рахує** твій реальний шанс та місце в черзі.\n"
        "4. **Візуалізує** дані графіками.\n\n"
        "**Технології:** Python, Aiogram, SQLAlchemy, Matplotlib.\n"
        "**Ліцензія:** Open Source (GPLv3).\n\n"
        "👨‍💻 **Автор:** [Олексій Одарчук](https://github.com/OlexiyOdarchuk)\n"
        "🛠 **Код:** [GitHub](https://github.com/OlexiyOdarchuk/AbitAssistant_bot)"
    )
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=kb.user_main)
