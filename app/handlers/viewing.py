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

import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

import app.keyboards as kb
import app.database.requests as rq
import app.services.stats as stats
from app.services.logger import log_user_action, log_admin_action, log_error
from app.states import States as st
from config import ADMIN_ID

router = Router()
change_page_text = "Натисніть на абітурієнта, щоб побачити повну інформацію\nНатисніть на кнопки керування або введіть бажану сторінку, щоб пересуватися сторінками\nНатисніть на номер сторінки, щоб повернутися до попереднього меню."


@router.callback_query(
    StateFilter(st.view_all, st.view_competitors), F.data == "applicant_back_to_stat"
)
async def back_to_stat(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username

        if user_id in ADMIN_ID:
            log_admin_action(user_id, "Returned to statistics from viewing")
        else:
            log_user_action(user_id, username, "Returned to statistics from viewing")

        await callback.message.delete()
        await state.set_state(st.choice_list)
        how_all_applicant = await stats.all_applicant_len(user_id)
        how_competitor_applicant = await stats.competitors_applicant_len(user_id)
        await callback.message.answer(
            f"""🔙 Повернення до статистики!
На цій освітній програмі наразі активно {how_all_applicant} бюджетних заявок.
Але лише {how_competitor_applicant} з них — це ваші справжні конкуренти 😉

📊 Використовуйте кнопки нижче, щоб дізнатись більше, або повертайтесь у головне меню для нової перевірки!
            """,
            reply_markup=kb.applicant_stat,
        )
    except Exception as e:
        log_error(e, f"Error in back_to_stat for user {callback.from_user.id}")


@router.callback_query(st.choice_list, F.data == "view_applicant_all")
async def view_applicant_all(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username

        if user_id in ADMIN_ID:
            log_admin_action(user_id, "Started viewing all applicants")
        else:
            log_user_action(user_id, username, "Started viewing all applicants")

        await state.set_state(st.view_all)
        keyboard = await kb.builder_applicant_all(user_id, 1)
        sent = await callback.message.edit_text(
            "📋 Всі бюджетні заяви на дану освітню програму", reply_markup=keyboard
        )
        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(e, f"Error in view_applicant_all for user {callback.from_user.id}")


@router.callback_query(st.choice_list, F.data == "view_applicant_competitors")
async def view_applicant_competitors(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username

        if user_id in ADMIN_ID:
            log_admin_action(user_id, "Started viewing competitors")
        else:
            log_user_action(user_id, username, "Started viewing competitors")

        await state.set_state(st.view_competitors)
        keyboard = await kb.builder_applicant_competitors(
            user_id, stats.user_score[user_id], 1
        )
        sent = await callback.message.edit_text(
            "🎯 Всі конкурентноспроможні заявки на дану освітню програму",
            reply_markup=keyboard,
        )
        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(
            e, f"Error in view_applicant_competitors for user {callback.from_user.id}"
        )


@router.callback_query(st.view_all, F.data.startswith("applicant_page_"))
async def change_page_all(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username
        page = int(callback.data.split("_")[-1])

        log_user_action(
            user_id, username, "Changed page in all applicants", f"Page: {page}"
        )

        keyboard = await kb.builder_applicant_all(user_id, page)
        sent = await callback.message.edit_text(change_page_text, reply_markup=keyboard)
        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(e, f"Error in change_page_all for user {callback.from_user.id}")


@router.callback_query(st.view_competitors, F.data.startswith("competitors_page_"))
async def change_page_competitors(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username
        page = int(callback.data.split("_")[-1])

        log_user_action(
            user_id, username, "Changed page in competitors", f"Page: {page}"
        )

        keyboard = await kb.builder_applicant_competitors(
            user_id, stats.user_score[user_id], page
        )
        sent = await callback.message.edit_text(change_page_text, reply_markup=keyboard)

        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(
            e, f"Error in change_page_competitors for user {callback.from_user.id}"
        )


@router.message(st.view_all)
async def change_page_at_message_all(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        await message.delete()

        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message_id")

        if last_bot_message_id:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=last_bot_message_id
                )
            except Exception as e:
                log_error(e, f"Failed to delete old bot message for user {user_id}")

        try:
            page = int(message.text)
            log_user_action(
                user_id,
                username,
                "Changed page via message in all applicants",
                f"Page: {page}",
            )
        except ValueError:
            log_user_action(
                user_id,
                username,
                "Invalid page number entered",
                f"Invalid input: {message.text}",
            )
            await message.answer("Будь ласка, введіть номер сторінки числом.")
            return

        keyboard = await kb.builder_applicant_all(user_id, page)

        sent = await message.answer(change_page_text, reply_markup=keyboard)

        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(
            e, f"Error in change_page_at_message_all for user {message.from_user.id}"
        )


@router.message(st.view_competitors)
async def change_page_at_message_competitors(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        await message.delete()

        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message_id")

        if last_bot_message_id:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=last_bot_message_id
                )
            except Exception as e:
                log_error(e, f"Failed to delete old bot message for user {user_id}")

        try:
            page = int(message.text)
            log_user_action(
                user_id,
                username,
                "Changed page via message in competitors",
                f"Page: {page}",
            )
        except ValueError:
            log_user_action(
                user_id,
                username,
                "Invalid page number entered",
                f"Invalid input: {message.text}",
            )
            await message.answer("Будь ласка, введіть номер сторінки числом.")
            return

        keyboard = await kb.builder_applicant_competitors(
            user_id, stats.user_score[user_id], page
        )

        sent = await message.answer(change_page_text, reply_markup=keyboard)

        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(
            e,
            f"Error in change_page_at_message_competitors for user {message.from_user.id}",
        )


@router.callback_query(
    StateFilter(st.view_all, st.view_competitors), F.data.startswith("applicant_")
)
async def all_info(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username

        await callback.answer()
        data = await rq.get_user_data(user_id)
        program_info = await rq.get_user_program_info(user_id)
        subjects_map = program_info.get("subjects_map", {})

        applicant_id = int(callback.data.split("_")[-1])
        applicants = [
            applicant for applicant in data if applicant.user_tg_id == user_id
        ]

        for applicant in applicants:
            if applicant.id == applicant_id:
                log_user_action(
                    user_id,
                    username,
                    "Viewed applicant details",
                    f"Applicant: {applicant.name}, ID: {applicant_id}",
                )

                formatted_detail = ""
                if applicant.subjects:
                    for sub_id, values in applicant.subjects.items():
                        # values is [score, flag, flag]
                        score_val = values[0] if isinstance(values, list) and len(values) > 0 else 0
                        sub_name = subjects_map.get(str(sub_id), f"Предмет {sub_id}")
                        formatted_detail += f"{sub_name}: {score_val}\n"
                else:
                    formatted_detail = "-"

                await callback.message.answer(
                    f"""📄 Повна інформація про абітурієнта:

👤 ПІП: {applicant.name}
📄 Статус заяви: {applicant.status}
🎯 Пріоритет на освітню програму: {applicant.priority}
📈 Конкурсний бал: {applicant.score if applicant.score else "-"}

📚 Бали НМТ:
{formatted_detail}

🔍 Конкурентність: {"✅ Конкурент" if applicant.competitor else "❌ Не конкурент"}
"""
                )
                break
    except Exception as e:
        log_error(e, f"Error in all_info for user {callback.from_user.id}")