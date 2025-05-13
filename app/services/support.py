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

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, bot
import app.keyboards as kb
from app.states import States as st

user_messages = {}

async def support(message: Message, state: FSMContext):
    """Приймає повідомлення від користувача для адміністрації"""
    await message.answer(
        "Надсилайте повідомлення для адміністрації (можна кілька: текст, фото, відео, голосові повідомлення і все інше). "
        "Коли будете готові — натисніть '📤 Відправити'.",
        reply_markup=kb.support,
    )
    await state.set_state(st.get_support)
    await state.update_data(messages=[])

async def collect_user_message(message: Message, state: FSMContext):
    data = await state.get_data()
    stored_messages = data.get("messages", [])

    stored_messages.append(message)
    await state.update_data(messages=stored_messages)

    await message.answer("✅ Повідомлення збережено. Ви можете додати ще або натиснути '📤 Відправити'.")

async def send_all_to_admin(message: Message, state: FSMContext):
    """Відправляє збережені повідомлення адміністраторам"""
    data = await state.get_data()
    messages = data.get("messages", [])

    if not messages:
        await message.answer("⚠️ Ви ще не надіслали жодного повідомлення.")
        return

    for admin in ADMIN_ID:
        await bot.send_message(
            chat_id=admin,
            text=f"📩 Нове звернення від {message.from_user.full_name} (Link: tg://user?id={message.from_user.id})",
        )

    for msg in messages:
        for admin in ADMIN_ID:
            try:
                forwarded = await msg.send_copy(chat_id=admin)
                user_messages[forwarded.message_id] = message.chat.id
            except Exception as e:
                await bot.send_message(
                    chat_id=admin,
                    text=f"❌ Помилка при надсиланні повідомлення: {e}"
                )

    await message.answer("✅ Ваші повідомлення надіслано адміністрації.", reply_markup=kb.user_main)
    await state.clear()


async def forward(message: Message, state: FSMContext):
    """Відправляє повідомлення відповіді адміністратора"""
    if message.reply_to_message:
        for admin in ADMIN_ID:
            if message.from_user.id == admin:
                original_chat_id = user_messages.get(message.reply_to_message.message_id)
                if original_chat_id:
                    try:
                        await bot.send_message(
                            chat_id=original_chat_id,
                            text="📬 Відповідь від адміністратора:"
                        )
                        await message.send_copy(chat_id=original_chat_id)
                    except Exception as e:
                        await bot.send_message(
                            chat_id=admin,
                            text=f"❌ Не вдалося надіслати відповідь: {e}"
                        )
                break
    elif message.from_user.id not in ADMIN_ID:
        for admin in ADMIN_ID:
            await bot.send_message(
                chat_id=admin,
                text=f"⚠️ Повідомлення від користувача {message.from_user.full_name} (Link: tg://user?id={message.from_user.id}):"
            )
            await message.send_copy(chat_id=admin)
