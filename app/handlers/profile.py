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
import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

import app.keyboards as kb
import app.database.requests as rq
from app.services.results_cache import save_result
from app.services.visualization import generate_rating_histogram
from app.states import ProfileStates as pst
from app.states import States as st
from app.services.logger import log_error
from config import bot

router = Router()


async def render_profile(message_or_callback, user_id: int, is_edit: bool = False):
    """
    Helper to render profile information.
    :param message_or_callback: Message or CallbackQuery object to use for reply/edit
    :param user_id: ID of the user
    :param is_edit: Whether to edit the existing message or send a new one
    """
    try:
        nmt_scores = await rq.get_user_nmt(user_id)
        settings = await rq.get_user_settings(user_id)

        formatted_nmt = ""
        if nmt_scores:
            for subject, score in nmt_scores.items():
                formatted_nmt += f"- {subject}: {score}\n"
        else:
            formatted_nmt = "❌ Не заповнено"

        quotas = settings.get("quotas", [])
        quotas_str = ", ".join(quotas) if quotas else "Немає"
        region_coef = "Так" if settings.get("region_coef") else "Ні"

        text = (
            f"👤 **Ваш профіль:**\n\n"
            f"📚 **Бали НМТ:**\n{formatted_nmt}\n"
            f"🎟 **Квоти:** {quotas_str}\n"
            f"🌍 **Регіональний коефіцієнт:** {region_coef}\n\n"
            f"Оберіть дію нижче 👇"
        )

        if is_edit:
            try:
                if isinstance(message_or_callback, CallbackQuery):
                    await message_or_callback.message.edit_text(
                        text, parse_mode="Markdown", reply_markup=kb.profile_main
                    )
                else:
                    await message_or_callback.edit_text(
                        text, parse_mode="Markdown", reply_markup=kb.profile_main
                    )
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e):
                    await message_or_callback.answer(
                        text, parse_mode="Markdown", reply_markup=kb.profile_main
                    )
        else:
            if isinstance(message_or_callback, CallbackQuery):
                await message_or_callback.message.answer(
                    text, parse_mode="Markdown", reply_markup=kb.profile_main
                )
            else:
                await message_or_callback.answer(
                    text, parse_mode="Markdown", reply_markup=kb.profile_main
                )

    except Exception as e:
        log_error(e, f"Error rendering profile for user {user_id}")


@router.message(F.text == "👤 Мій профіль")
async def open_profile(message: Message):
    await render_profile(message, message.from_user.id, is_edit=False)


# --- Редагування НМТ ---


@router.callback_query(F.data == "edit_nmt")
async def start_edit_nmt(callback: CallbackQuery, state: FSMContext):
    try:
        user_nmt = await rq.get_user_nmt(callback.from_user.id)
        await callback.message.answer(
            "Оберіть предмет:", reply_markup=kb.get_subjects_kb(user_nmt)
        )
        await state.set_state(pst.choose_subject)
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in start_edit_nmt")


@router.message(pst.choose_subject, F.text)
async def choose_subject(message: Message, state: FSMContext):
    try:
        if message.text == "❌ До головного меню":
            await state.clear()
            await message.answer("Головне меню", reply_markup=kb.user_main)
            return

        user_nmt = await rq.get_user_nmt(message.from_user.id)

        if message.text == "✅ Завершити введення":
            required = {"Українська мова", "Математика", "Історія України"}
            filled = set(user_nmt.keys())

            missing = required - filled
            if missing:
                await message.answer(
                    f"❌ Ви не ввели бали з обов'язкових предметів: {', '.join(missing)}"
                )
                return

            if len(filled) != 4:
                await message.answer(
                    f"❌ Повинно бути рівно 4 предмети (3 обов'язкових + 1 на вибір). Зараз введено: {len(filled)}"
                )
                return

            await state.clear()
            await render_profile(message, message.from_user.id, is_edit=False)
            return

        clean_subject = message.text.replace("✅ ", "")
        valid_subjects = [
            "Українська мова",
            "Математика",
            "Історія України",
            "Англійська мова",
            "Біологія",
            "Фізика",
            "Хімія",
            "Географія",
            "Українська література",
            "Інша іноземна",
        ]

        if clean_subject not in valid_subjects:
            await message.answer("❌ Будь ласка, оберіть предмет з клавіатури.")
            return

        if "✅ " in message.text:
            await message.answer(
                f"Предмет '{clean_subject}' вже додано. Що хочете зробити?",
                reply_markup=kb.edit_or_delete_subject_kb(clean_subject),
            )
            return

        await state.update_data(current_subject=clean_subject)
        await message.answer(
            f"Введіть ваш бал з предмету '{clean_subject}' (100-200):",
            reply_markup=kb.remove_keyboard,
        )
        await state.set_state(pst.enter_score)
    except Exception as e:
        log_error(e, "Error in choose_subject")


@router.callback_query(F.data.startswith("edit_subj_"))
async def edit_existing_subject(callback: CallbackQuery, state: FSMContext):
    try:
        subject = callback.data.split("edit_subj_")[1]
        await state.update_data(current_subject=subject)
        await callback.message.edit_text(
            f"Введіть новий бал з предмету '{subject}' (100-200):"
        )
        await state.set_state(pst.enter_score)
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in edit_existing_subject")


@router.callback_query(F.data.startswith("del_subj_"))
async def delete_existing_subject(callback: CallbackQuery):
    try:
        subject = callback.data.split("del_subj_")[1]
        user_id = callback.from_user.id

        user_nmt = await rq.get_user_nmt(user_id)
        if subject in user_nmt:
            del user_nmt[subject]
            await rq.set_user_nmt(user_id, user_nmt)

        await callback.message.delete()
        await callback.message.answer(
            f"🗑 Предмет '{subject}' видалено.",
            reply_markup=kb.get_subjects_kb(user_nmt),
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in delete_existing_subject")


@router.callback_query(F.data == "cancel_subj_edit")
async def cancel_subj_edit(callback: CallbackQuery):
    try:
        await callback.message.delete()
        await callback.answer()
    except Exception:
        pass


@router.message(pst.enter_score)
async def enter_score(message: Message, state: FSMContext):
    try:
        score_text = message.text.replace(",", ".")
        score = float(score_text)

        if not (100 <= score <= 200):
            await message.answer(
                "❌ Бал повинен бути в межах від 100 до 200. Спробуйте ще раз."
            )
            return

        data = await state.get_data()
        subject = data.get("current_subject")

        current_nmt = await rq.get_user_nmt(message.from_user.id)
        current_nmt[subject] = score
        await rq.set_user_nmt(message.from_user.id, current_nmt)

        await message.answer(
            f"✅ Збережено: {subject} - {score}",
            reply_markup=kb.get_subjects_kb(current_nmt),
        )
        await state.set_state(pst.choose_subject)
    except ValueError:
        await message.answer("❌ Помилка. Введіть число (наприклад, 175.5).")
    except Exception as e:
        log_error(e, "Error in enter_score")


# --- Налаштування (Квоти та РК) ---


@router.callback_query(F.data == "edit_settings")
async def edit_settings_menu(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "⚙️ **Налаштування профілю**\nОберіть категорію для редагування:",
            parse_mode="Markdown",
            reply_markup=kb.settings_kb,
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in edit_settings_menu")


@router.callback_query(F.data == "back_to_profile")
async def back_to_profile_cb(callback: CallbackQuery):
    await render_profile(callback, callback.from_user.id, is_edit=True)
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings_cb(callback: CallbackQuery):
    await edit_settings_menu(callback)


# -- Квоти --
@router.callback_query(F.data == "settings_quotas")
async def settings_quotas(callback: CallbackQuery):
    try:
        settings = await rq.get_user_settings(callback.from_user.id)
        quotas = settings.get("quotas", [])

        await callback.message.edit_text(
            "🎟 **Налаштування квот**\nНатисніть на кнопку, щоб увімкнути/вимкнути квоту.",
            parse_mode="Markdown",
            reply_markup=kb.get_quotas_kb(quotas),
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in settings_quotas")


@router.callback_query(F.data.startswith("toggle_quota_"))
async def toggle_quota(callback: CallbackQuery):
    try:
        quota = callback.data.split("_")[-1]
        user_id = callback.from_user.id

        settings = await rq.get_user_settings(user_id)
        current_quotas = settings.get("quotas", [])

        if quota in current_quotas:
            current_quotas.remove(quota)
        else:
            current_quotas.append(quota)

        settings["quotas"] = current_quotas
        await rq.set_user_settings(user_id, settings)

        await callback.message.edit_reply_markup(
            reply_markup=kb.get_quotas_kb(current_quotas)
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in toggle_quota")


# -- Регіональний коефіцієнт --
@router.callback_query(F.data == "settings_region")
async def settings_region(callback: CallbackQuery):
    try:
        settings = await rq.get_user_settings(callback.from_user.id)
        is_active = settings.get("region_coef", False)

        await callback.message.edit_text(
            "🌍 **Регіональний коефіцієнт**\nЧи застосовувати регіональний коефіцієнт (РК) при розрахунках?",
            parse_mode="Markdown",
            reply_markup=kb.get_region_kb(is_active),
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in settings_region")


@router.callback_query(F.data == "toggle_region_coef")
async def toggle_region(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        settings = await rq.get_user_settings(user_id)

        new_state = not settings.get("region_coef", False)
        settings["region_coef"] = new_state

        await rq.set_user_settings(user_id, settings)

        await callback.message.edit_reply_markup(
            reply_markup=kb.get_region_kb(new_state)
        )
        await callback.answer(f"РК {'увімкнено' if new_state else 'вимкнено'}")
    except Exception as e:
        log_error(e, "Error in toggle_region")


# --- Збережені списки ---


@router.callback_query(F.data == "saved_lists")
async def show_saved_lists(callback: CallbackQuery):
    try:
        lists = await rq.get_saved_lists(callback.from_user.id)
        if not lists:
            await callback.answer("У вас немає збережених списків.", show_alert=True)
            await render_profile(callback, callback.from_user.id, is_edit=True)
            return

        builder = InlineKeyboardBuilder()
        for item in lists:
            btn_text = f"📂 {item.name[:30]}"
            builder.button(text=btn_text, callback_data=f"manage_list_{item.id}")

        builder.button(text="⬅️ Назад", callback_data="back_to_profile")
        builder.adjust(1)

        try:
            await callback.message.edit_text(
                "📂 **Ваші збережені списки:**",
                parse_mode="Markdown",
                reply_markup=builder.as_markup(),
            )
        except TelegramBadRequest:
            await callback.message.delete()
            await callback.message.answer(
                "📂 **Ваші збережені списки:**",
                parse_mode="Markdown",
                reply_markup=builder.as_markup(),
            )

        await callback.answer()
    except Exception as e:
        log_error(e, "Error in show_saved_lists")


@router.callback_query(F.data.startswith("manage_list_"))
async def manage_list(callback: CallbackQuery):
    try:
        list_id = int(callback.data.split("_")[-1])
        saved_list = await rq.get_saved_list(list_id)

        if not saved_list:
            await callback.answer("Не знайдено")
            await show_saved_lists(callback)
            return

        text = (
            f"📂 **Список: {saved_list.name}**\n"
            f"📅 Створено: {saved_list.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Оберіть дію 👇"
        )

        builder = InlineKeyboardBuilder()
        builder.button(text="👁 Переглянути", callback_data=f"load_list_{list_id}")
        builder.button(text="🔗 Поділитися", callback_data=f"share_list_{list_id}")
        builder.button(text="📤 Експорт в JSON", callback_data=f"export_list_{list_id}")
        builder.button(text="🗑 Видалити", callback_data=f"delete_list_{list_id}")
        builder.button(text="⬅️ Назад", callback_data="saved_lists")
        builder.adjust(1)

        await callback.message.edit_text(
            text, parse_mode="Markdown", reply_markup=builder.as_markup()
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in manage_list")


@router.callback_query(F.data.startswith("load_list_"))
async def load_saved_list(callback: CallbackQuery, state: FSMContext):
    try:
        list_id = int(callback.data.split("_")[-1])
        saved_list = await rq.get_saved_list(list_id)
        if saved_list:
            # Конвертуємо ключи зі str назад в int (JSON конвертує int ключі в str)
            data = saved_list.data
            requests = data.get("requests", {})
            if requests:
                competitors = requests.get("competitors", {})
                non_competitors = requests.get("non-competitors", {})

                # Конвертуємо ключі зі str в int
                data["requests"]["competitors"] = {
                    int(k) if isinstance(k, str) and k.isdigit() else k: v
                    for k, v in competitors.items()
                }
                data["requests"]["non-competitors"] = {
                    int(k) if isinstance(k, str) and k.isdigit() else k: v
                    for k, v in non_competitors.items()
                }

            save_result(callback.from_user.id, data)
            analysis = data.get("analysis", {})
            chance = analysis.get("chance", "Unknown")
            advice = analysis.get("advice", "")
            my_rank = analysis.get("my_real_rank", "?")
            budget_spots = analysis.get("remaining_general", "?")
            user_rating = data.get("user_rating_score", 0)

            chance_emoji = {
                "High": "🟢 Високий",
                "High (Quota 1)": "🟢 Високий (Квота 1)",
                "High (Quota 2)": "🟢 Високий (Квота 2)",
                "Medium": "🟡 Середній",
                "Low": "🔴 Низький",
                "Zero": "⚫ Нульовий",
            }.get(chance, chance)

            loop = asyncio.get_running_loop()
            title = f"Рейтинг: {saved_list.name[:20]}"

            photo = await loop.run_in_executor(
                None, generate_rating_histogram, data, user_rating, title
            )

            caption = (
                f"📂 Завантажено: **{saved_list.name}**\n\n"
                f"🎯 **Ваш рейтинговий бал:** {user_rating:.3f}\n"
                f"🏆 **Ваше реальне місце:** {my_rank} (на {budget_spots} вільних місць)\n"
                f"🎲 **Шанс на вступ:** {chance_emoji}\n\n"
                f"💡 **Вердикт:** {advice}"
            )

            await callback.message.delete()

            if photo:
                await callback.message.answer_photo(
                    photo,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=kb.applicant_stat,
                )
            else:
                await callback.message.answer(
                    caption, parse_mode="Markdown", reply_markup=kb.applicant_stat
                )

            await state.set_state(st.choice_list)
            await callback.answer()
    except Exception as e:
        log_error(e, "Error in load_saved_list")
        await callback.answer("Помилка при завантаженні списку.")


@router.callback_query(F.data.startswith("share_list_"))
async def share_list(callback: CallbackQuery):
    try:
        list_id = int(callback.data.split("_")[-1])
        bot_info = await bot.get_me()
        share_link = f"https://t.me/{bot_info.username}?start=list_{list_id}"

        await callback.message.answer(
            f"🔗 **Ваше посилання для шерингу:**\n\n`{share_link}`\n\n"
            f"Будь-хто, хто перейде за цим посиланням, отримає копію вашого аналізу у свій профіль.",
            parse_mode="Markdown",
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in share_list")


@router.callback_query(F.data.startswith("delete_list_"))
async def delete_list(callback: CallbackQuery):
    try:
        list_id = int(callback.data.split("_")[-1])
        await rq.delete_saved_list(list_id)
        await callback.answer("🗑 Список видалено")
        await show_saved_lists(callback)
    except Exception as e:
        log_error(e, "Error in delete_list")


@router.callback_query(F.data.startswith("export_list_"))
async def export_list(callback: CallbackQuery):
    try:
        list_id = int(callback.data.split("_")[-1])
        saved_list = await rq.get_saved_list(list_id)

        if not saved_list:
            await callback.answer("Помилка")
            return

        json_data = json.dumps(saved_list.data, indent=2, ensure_ascii=False)
        file_content = BufferedInputFile(
            json_data.encode("utf-8"), filename=f"analysis_{list_id}.json"
        )

        await callback.message.answer_document(
            file_content,
            caption=f"📤 Повний експорт даних для списку: **{saved_list.name}**",
            parse_mode="Markdown",
        )
        await callback.answer()
    except Exception as e:
        log_error(e, "Error in export_list")
