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
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.services.mailing as mail
from app.states import States as st
import app.services.stats as stats
from app.services.logger import (
    log_admin_action,
    log_error,
    get_log_files,
    get_log_content,
)
from app.services.user_management import get_users_with_links
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    """Перевіряє чи є користувач адміністратором"""
    return user_id in ADMIN_ID


@router.message(F.text == "📣 Розсилка")
async def mailing(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        log_admin_action(message.from_user.id, "Started mailing process")
        await mail.mailing(message, state)
    except Exception as e:
        log_error(e, f"Error in mailing command for admin {message.from_user.id}")
        await message.answer("❌ Помилка при розсилці")


@router.message(st.get_mailing)
async def get_mailing_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        log_admin_action(
            message.from_user.id,
            "Entered mailing text",
            f"Text length: {len(message.text)}",
        )
        await mail.get_mailing_text(message, state)
    except Exception as e:
        log_error(e, f"Error in get_mailing_text for admin {message.from_user.id}")
        await message.answer("❌ Помилка при обробці тексту")


@router.message(st.init_mailing, F.text == "📣 Відправити розсилку")
async def init(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        log_admin_action(message.from_user.id, "Sent mailing")
        await mail.init(message, state)
    except Exception as e:
        log_error(e, f"Error in init mailing for admin {message.from_user.id}")
        await message.answer("❌ Помилка при відправці розсилки")


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message):
    if not is_admin(message.from_user.id):
        return

    try:
        log_admin_action(message.from_user.id, "Viewed statistics")
        await message.answer(await stats.admin_statistics())
    except Exception as e:
        log_error(e, f"Error in statistics command for admin {message.from_user.id}")
        await message.answer("❌ Помилка при отриманні статистики")


@router.message(F.text == "👥 Користувачі")
async def users_menu(message: Message):
    """Меню управління користувачами"""
    if not is_admin(message.from_user.id):
        return

    try:
        log_admin_action(message.from_user.id, "Viewed users list")

        users_text = await get_users_with_links(limit=50)
        await message.answer(users_text, parse_mode="Markdown")

    except Exception as e:
        log_error(e, f"Error in users_menu for admin {message.from_user.id}")
        await message.answer("❌ Помилка отримання списку користувачів")


@router.message(F.text == "📋 Логи")
async def logs_menu(message: Message):
    """Меню перегляду логів"""
    if not is_admin(message.from_user.id):
        return

    try:
        log_admin_action(message.from_user.id, "Opened logs menu")

        log_files = get_log_files()

        if not log_files:
            await message.answer("📋 Логи не знайдено")
            return

        builder = InlineKeyboardBuilder()

        for filename, file_info in log_files.items():
            size_text = f"{file_info['size_mb']}MB"
            builder.add(
                InlineKeyboardButton(
                    text=f"📄 {filename} ({size_text})",
                    callback_data=f"log_view_{filename}",
                )
            )

        builder.add(
            InlineKeyboardButton(
                text="📥 Завантажити всі логи", callback_data="logs_download_all"
            )
        )

        await message.answer(
            "📋 **Система логування**\n\nДоступні лог файли:",
            reply_markup=builder.as_markup(),
        )
    except Exception as e:
        log_error(e, f"Error in logs_menu for admin {message.from_user.id}")


@router.callback_query(F.data.startswith("log_view_"))
async def log_view_callback_handler(callback):
    """Обробник для перегляду логів"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено")
        return

    filename = callback.data.split("log_view_")[1]
    log_admin_action(callback.from_user.id, "Viewed log file", f"File: {filename}")

    log_content = get_log_content(filename, 50)  # Останні 50 рядків

    if log_content:
        if len(log_content) > 4000:
            # Якщо лог занадто великий, відправляємо файл
            log_file = FSInputFile(f"logs/{filename}")
            await callback.message.answer_document(
                log_file, caption=f"📋 Лог файл: {filename}"
            )
        else:
            await callback.message.answer(
                f"📋 **Лог файл: {filename}**\n\n```\n{log_content}\n```"
            )
    else:
        await callback.message.answer("❌ Помилка читання лог файлу")

    await callback.answer()


@router.callback_query(F.data == "logs_download_all")
async def download_all_logs_callback_handler(callback):
    """Обробник для завантаження всіх логів"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено")
        return

    log_admin_action(callback.from_user.id, "Downloaded all logs")

    log_files = get_log_files()

    if not log_files:
        await callback.message.answer("❌ Логи не знайдено")
        await callback.answer()
        return

    # Відправляємо кожен лог файл окремо
    for filename in log_files.keys():
        try:
            log_file = FSInputFile(f"logs/{filename}")
            await callback.message.answer_document(log_file, caption=f"📋 {filename}")
        except Exception as e:
            await callback.message.answer(
                f"❌ Помилка завантаження {filename}: {str(e)}"
            )

    await callback.answer("📥 Всі логи відправлено")
