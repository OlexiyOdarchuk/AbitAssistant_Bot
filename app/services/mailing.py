import asyncio
import time

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, bot
import app.database.requests as rq
import app.keyboards as kb
from app.states import States as st


async def mailing(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await message.answer(
            "📣 Надішліть текст розсилки: 📣", reply_markup=kb.return_back
        )
        await state.set_state(st.get_mailing)
    else:
        await message.answer(
            "У вас немає прав на використання цієї команди, ви повертаєтеся в головне меню."
        )
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main,
        )


async def get_mailing_text(message: Message, state: FSMContext):
    await state.update_data(mailing_text=message.md_text)
    await message.answer("Текст прийнято, повідомлення виглядає ось так:")
    data = await state.get_data()
    mailing_text = data.get("mailing_text", "Текст не знайдено!!!")
    await message.answer(
        f"📣Повідомлення з розсилки: \n\n{mailing_text}", reply_markup=kb.mailing
    )
    await state.set_state(st.init_mailing)


async def init(message: Message, state: FSMContext):
    data = await state.get_data()
    mailing_text = data.get("mailing_text", "Текст не знайдено!!!")
    users = await rq.get_users()
    start_time = time.time()
    sent_count = 0
    for user in users:
        try:
            await bot.send_message(
                chat_id=user, text=f"📣Повідомлення з розсилки: \n\n{mailing_text}"
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
            text=f"Розсилка завершена! \nВідправлено {sent_count} повідомлень за {elapsed_time} секунд.",
            reply_markup=kb.admin_main,
        )
    await state.set_state(None)
