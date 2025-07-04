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
import time

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, bot
import app.database.requests as rq
import app.keyboards as kb
from app.states import States as st


async def mailing(message: Message, state: FSMContext):
    """Отримує повідомлення для розсилки"""
    if message.from_user.id in ADMIN_ID:
        await message.answer(
            "📣 Надішліть текст або фото з підписом для розсилки:", reply_markup=kb.return_back
        )
        await state.set_state(st.get_mailing)
    else:
        await message.answer(
            "У вас немає прав на використання цієї команди, ви повертаєтеся в головне меню."
        )
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче 👇",
            reply_markup=kb.user_main,
        )


async def get_mailing_text(message: Message, state: FSMContext):
    """Сортує повідомлення для розсилки за типом"""
    if message.photo:
        photo_id = message.photo[-1].file_id
        caption = message.caption or ""
        await state.update_data(mailing_text=caption, mailing_photo=photo_id)
        await message.answer_photo(photo=photo_id, caption=f"📣 Повідомлення з розсилки:\n\n{caption}", reply_markup=kb.mailing)
    elif message.text:
        await state.update_data(mailing_text=message.text, mailing_photo=None)
        await message.answer(f"📣 Повідомлення з розсилки:\n\n{message.text}", reply_markup=kb.mailing)
    elif message.video:
        video_id = message.video.file_id
        caption = message.caption or ""
        await state.update_data(mailing_text=caption, mailing_video=video_id)
        await message.answer_video(video=video_id, caption=f"📣 Повідомлення з розсилки:\n\n{caption}", reply_markup=kb.mailing)
    else:
        await message.answer("Будь ласка, надішліть текст або фото з підписом.")
        return

    await state.set_state(st.init_mailing)


async def init(message: Message, state: FSMContext):
    """Починаємо розсилку"""
    data = await state.get_data()
    mailing_text = data.get("mailing_text", "Текст не знайдено!!!")
    mailing_photo = data.get("mailing_photo", None)
    mailing_video = data.get("mailing_video", None)
    users = await rq.get_users()
    start_time = time.time()
    sent_count = 0
    for user in users:
        try:
            if mailing_photo:
                await bot.send_photo(
                    chat_id=user,
                    photo=mailing_photo,
                    caption=f"📣 Повідомлення з розсилки:\n\n{mailing_text}"
                )
            elif mailing_video:
                await bot.send_video(
                    chat_id=user,
                    video=mailing_video,
                    caption=f"📣 Повідомлення з розсилки:\n\n{mailing_text}"
                )
            else:
                await bot.send_message(
                    chat_id=user,
                    text=f"📣 Повідомлення з розсилки:\n\n{mailing_text}"
                )
            sent_count += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            for admin in ADMIN_ID:
                await bot.send_message(
                    chat_id=admin,
                    text=f"Помилка при відправці користувачу tg://user?id={user}: {e}",
                )

    elapsed_time = round(time.time() - start_time, 2)
    for admin in ADMIN_ID:
        await bot.send_message(
            chat_id=admin,
            text=f"Розсилка завершена! ✅\nВідправлено {sent_count} повідомлень за {elapsed_time} секунд.",
            reply_markup=kb.admin_main,
        )
    await state.clear()
