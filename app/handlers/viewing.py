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
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest

import app.keyboards as kb
import app.database.requests as rq
from app.services.results_cache import get_result, save_result
from app.services.filter import recalculate_analysis, get_cached_competitor
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

        # Отримуємо свіжі дані з кешу
        result = get_result(user_id)
        if not result:
            await callback.message.answer(
                "⚠️ Дані сесії втрачено. Будь ласка, почніть аналіз знову.",
                reply_markup=kb.user_main,
            )
            return

        analysis = result.get("analysis", {})
        my_rank = analysis.get("my_real_rank", "?")
        remaining = analysis.get("remaining_general", "?")
        chance = analysis.get("chance", "?")

        chance_emoji = {
            "High": "🟢 Високий",
            "High (Quota 1)": "🟢 Високий (Квота 1)",
            "High (Quota 2)": "🟢 Високий (Квота 2)",
            "Medium": "🟡 Середній",
            "Low": "🔴 Низький",
            "Zero": "⚫ Нульовий",
        }.get(chance, chance)

        await callback.message.answer(
            f"🔙 **Повернення до статистики!**\n\n"
            f"🏆 **Ваше реальне місце:** {my_rank} (на {remaining} вільних місць)\n"
            f"🎲 **Шанс:** {chance_emoji}\n\n"
            f"📊 Використовуйте кнопки нижче, щоб дізнатись більше.",
            parse_mode="Markdown",
            reply_markup=kb.applicant_stat,
        )
    except Exception as e:
        log_error(e, f"Error in back_to_stat for user {callback.from_user.id}")
        await callback.answer("Сталася помилка при поверненні.")


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

        await callback.message.delete()
        sent = await callback.message.answer(
            "📋 **Всі бюджетні заяви на дану освітню програму**",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        await callback.answer()
    except Exception as e:
        log_error(e, f"Error in view_applicant_all for user {callback.from_user.id}")
        await callback.answer("Не вдалося завантажити список.")


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
        keyboard = await kb.builder_applicant_competitors(user_id, 0.0, 1)

        await callback.message.delete()
        sent = await callback.message.answer(
            "🎯 **Всі конкурентноспроможні заявки**",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        await state.update_data(last_bot_message_id=sent.message_id)
        await callback.answer()
    except Exception as e:
        log_error(
            e, f"Error in view_applicant_competitors for user {callback.from_user.id}"
        )
        await callback.answer("Не вдалося завантажити список конкурентів.")


@router.callback_query(st.view_all, F.data.startswith("applicant_page_"))
async def change_page_all(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        page = int(callback.data.split("_")[-1])
        keyboard = await kb.builder_applicant_all(user_id, page)
        await callback.message.edit_text(change_page_text, reply_markup=keyboard)
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in change_page_all")


@router.callback_query(st.view_competitors, F.data.startswith("competitors_page_"))
async def change_page_competitors(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        page = int(callback.data.split("_")[-1])
        keyboard = await kb.builder_applicant_competitors(user_id, 0.0, page)
        await callback.message.edit_text(change_page_text, reply_markup=keyboard)
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in change_page_competitors")


@router.message(st.view_all)
async def change_page_at_message_all(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        await message.delete()

        try:
            page = int(message.text)
        except ValueError:
            return

        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message_id")

        keyboard = await kb.builder_applicant_all(user_id, page)

        if last_bot_message_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    text=change_page_text,
                    reply_markup=keyboard,
                )
                return
            except Exception:
                pass

        sent = await message.answer(change_page_text, reply_markup=keyboard)
        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(e, "Error in change_page_at_message_all")


@router.message(st.view_competitors)
async def change_page_at_message_competitors(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        await message.delete()

        try:
            page = int(message.text)
        except ValueError:
            return

        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message_id")

        keyboard = await kb.builder_applicant_competitors(user_id, 0.0, page)

        if last_bot_message_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    text=change_page_text,
                    reply_markup=keyboard,
                )
                return
            except Exception:
                pass

        sent = await message.answer(change_page_text, reply_markup=keyboard)
        await state.update_data(last_bot_message_id=sent.message_id)
    except Exception as e:
        log_error(e, "Error in change_page_at_message_competitors")


async def render_applicant_details(callback: CallbackQuery, applicant_id: int):
    """Helper to render applicant details to avoid code duplication."""
    try:
        user_id = callback.from_user.id
        result = get_result(user_id)
        if not result:
            await callback.message.answer("⚠️ Дані сесії втрачено.")
            return

        competitors = result.get("requests", {}).get("competitors", {})
        non_competitors = result.get("requests", {}).get("non-competitors", {})

        # JSON може конвертувати числові ключі в рядки, спробуємо обидва варіанти
        target_app = competitors.get(applicant_id) or non_competitors.get(applicant_id)
        if not target_app:
            # Спробуємо як рядок
            target_app = competitors.get(str(applicant_id)) or non_competitors.get(
                str(applicant_id)
            )

        if target_app:
            is_threat = applicant_id in competitors
            filter_reason = target_app.get("filter_reason", "Real Threat")
            status_icon = "🔴 ЗАГРОЗА" if is_threat else "🟢 НЕ ЗАГРОЗА"

            # Деталі предметів
            formatted_detail = ""
            detail_scores = target_app.get("detail_scores", {})
            if detail_scores:
                for subj, score in detail_scores.items():
                    formatted_detail += f"📘 {subj}: {score}\n"
            else:
                formatted_detail = "Деталі відсутні"

            text = (
                f"📄 **Інформація про абітурієнта:**\n\n"
                f"👤 **ПІП:** {target_app.get('name')}\n"
                f"📊 **Статус:** {status_icon}\n"
                f"💡 **Причина:** {filter_reason}\n\n"
                f"🎯 **Пріоритет:** {target_app.get('priority')}\n"
                f"📈 **Конкурсний бал:** {target_app.get('score')}\n"
                f"🏫 **Статус заяви:** {target_app.get('status')}\n\n"
                f"📚 **Бали НМТ:**\n{formatted_detail}\n"
                f"🔗 [Посилання на abit-poisk]({target_app.get('abit_link', '#')})"
            )

            keyboard = kb.builder_applicant_details(applicant_id, is_threat)
            try:
                await callback.message.edit_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                )
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e):
                    await callback.message.answer(
                        text,
                        parse_mode="Markdown",
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                    )
        else:
            await callback.answer("Абітурієнта не знайдено.", show_alert=True)
    except Exception as e:
        log_error(e, "Error rendering applicant details")


@router.callback_query(
    StateFilter(st.view_all, st.view_competitors), F.data.regexp(r"^applicant_\d+$")
)
async def all_info(callback: CallbackQuery):
    try:
        applicant_id = int(callback.data.split("_")[-1])
        await render_applicant_details(callback, applicant_id)
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in all_info callback")


@router.callback_query(F.data.startswith("toggle_threat_"))
async def toggle_threat(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        applicant_id = int(callback.data.split("_")[-1])

        result = get_result(user_id)
        if not result:
            await callback.answer("Дані втрачено", show_alert=True)
            return

        competitors = result.get("requests", {}).get("competitors", {})
        non_competitors = result.get("requests", {}).get("non-competitors", {})

        is_threat = applicant_id in competitors
        if not is_threat:
            is_threat = str(applicant_id) in competitors

        target_app = competitors.get(applicant_id) or non_competitors.get(applicant_id)
        if not target_app:
            # Спробуємо як рядок
            target_app = competitors.get(str(applicant_id)) or non_competitors.get(
                str(applicant_id)
            )

        if not target_app:
            await callback.answer("Помилка: не знайдено", show_alert=True)
            return

        # Визначимо, в якому форматі ключ (int чи str)
        app_key = applicant_id
        if applicant_id not in competitors and applicant_id not in non_competitors:
            if str(applicant_id) in competitors or str(applicant_id) in non_competitors:
                app_key = str(applicant_id)

        if is_threat:
            if app_key in competitors:
                del competitors[app_key]
            target_app["filter_reason"] = "Manual override (Not Threat)"
            non_competitors[app_key] = target_app
            await callback.answer("✅ Позначено як НЕ конкурент")
        else:
            if app_key in non_competitors:
                del non_competitors[app_key]
            target_app["filter_reason"] = "Manual override (Real Threat)"
            competitors[app_key] = target_app
            await callback.answer("✅ Позначено як КОНКУРЕНТ")

        new_result = await recalculate_analysis(result, user_id)
        save_result(user_id, new_result)

        await render_applicant_details(callback, applicant_id)

    except Exception as e:
        log_error(e, "Error toggling threat")
        await callback.answer("Помилка при зміні статусу.")


@router.callback_query(F.data.startswith("show_abit_history_"))
async def show_abit_history(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        applicant_id = int(callback.data.split("_")[-1])

        result = get_result(user_id)
        if not result:
            await callback.answer("Дані втрачено", show_alert=True)
            return

        competitors = result.get("requests", {}).get("competitors", {})
        non_competitors = result.get("requests", {}).get("non-competitors", {})
        target_app = competitors.get(applicant_id) or non_competitors.get(applicant_id)

        if not target_app:
            # Спробуємо як рядок
            target_app = competitors.get(str(applicant_id)) or non_competitors.get(
                str(applicant_id)
            )

        if not target_app:
            await callback.answer("Абітурієнта не знайдено")
            return

        name = target_app.get("name")
        await callback.answer("🔍 Завантажую історію...")

        history = await get_cached_competitor(name)
        if not history:
            from app.services.parse_abit_poisk import fetch_applicant_data
            from app.database.requests import cache_competitor

            history = await fetch_applicant_data(name)
            if history:
                await cache_competitor(name, history)

        if not history:
            await callback.message.answer(f"📭 Не знайдено інших заяв для {name}")
            return

        text = f"📋 **Історія заяв: {name}**\n\n"
        try:
            history.sort(
                key=lambda x: (
                    int(x.get("priority", 99))
                    if str(x.get("priority")).isdigit()
                    else 99
                )
            )
        except Exception:
            pass

        for item in history[:10]:
            status = item.get("status", "")
            status_emoji = (
                "✅"
                if "до наказу" in status.lower() or "рекомендовано" in status.lower()
                else "⏳"
            )
            text += (
                f"{status_emoji} **#{item.get('priority', '-')}** | {item.get('university', '')[:20]}...\n"
                f"   └ {item.get('specialty', '')[:30]}... (Бал: {item.get('total_score', '-')})\n"
                f"   └ Статус: {status}\n\n"
            )

        if len(history) > 10:
            text += f"...та ще {len(history) - 10} заяв."

        await callback.message.answer(text, parse_mode="Markdown")

    except Exception as e:
        log_error(e, "Error showing history")
        await callback.answer("Помилка завантаження історії.")


@router.callback_query(F.data == "applicant_back_to_list")
async def back_to_list(callback: CallbackQuery, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state == st.view_competitors:
            await view_applicant_competitors(callback, state)
        else:
            await view_applicant_all(callback, state)
    except Exception as e:
        log_error(e, "Error returning to list")
        await callback.answer("Помилка при поверненні.")


@router.callback_query(F.data == "save_list")
async def save_current_list(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        result = get_result(user_id)

        if not result:
            await callback.answer("Нічого зберігати", show_alert=True)
            return

        name = f"{result.get('university_name', 'Unknown')} | {result.get('spec_code', '')} {result.get('program_name', '')}"
        name = name[:50] + "..." if len(name) > 50 else name
        url = result.get("url", "https://vstup.osvita.ua/")

        await rq.save_specialty_list(user_id, name, url, result)
        await callback.answer("✅ Список успішно збережено в профілі!", show_alert=True)

    except Exception as e:
        log_error(e, "Error saving list")
        await callback.answer("Помилка при збереженні", show_alert=True)
