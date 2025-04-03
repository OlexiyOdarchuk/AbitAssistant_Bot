from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, bot
import app.keyboards as kb
from app.states import States as st

user_messages = {}

async def support(message: Message, state: FSMContext):
    await message.answer(
        "Наступне повідомлення буде відправлено адміністрації, формулюйте його уважно:",
        reply_markup=kb.return_back,
    )
    await state.set_state(st.get_support)

async def get_support_text(message: Message, state: FSMContext):
    if message.text=="❌ До головного меню":
        await state.set_state(None)
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main)
    else:
        await message.answer(
            "Ваше повідомлення зареєстровано, дякую за відгук. \nВам дадуть відповідь найближчим часом."
        )
        await state.set_state(None)
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main,
        )

        try:
            forwarded_message = await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Повідомлення від користувача {message.from_user.url}:\n\n{message.text}\n\nБуло надіслано в З'вязок"
            )
            
            user_messages[forwarded_message.message_id] = message.chat.id

        except Exception as e:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Помилка при відправці повідомлення від користувача {message.from_user.url}: {e}",
            )


async def forward(message: Message, state: FSMContext):
    if message.reply_to_message and message.from_user.id == ADMIN_ID:
        original_chat_id = user_messages.get(message.reply_to_message.message_id)
        if original_chat_id:
            await bot.send_message(original_chat_id, f"Адміністратор відповів: {message.text}")
    if message.from_user.id != ADMIN_ID:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Повідомлення від користувача {message.from_user.url}:\n\n{message.md_text} \n\nБуло надіслано випадково",
        )
        
        
# async def support(message: Message, state: FSMContext):
#     await message.answer(
#         "Наступне повідомлення буде відправлено адміністрації, формулюйте його уважно:",
#         reply_markup=kb.return_back,
#     )
#     await state.set_state(st.get_support)


# async def get_support_text(message: Message, state: FSMContext):
#     await message.answer(
#         "Ваше повідомлення зареєстровано, дякую за відгук. \nВам дадуть відповідь найближчим часом."
#     )
#     await state.set_state(None)
#     await message.answer(
#         "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
#         reply_markup=kb.user_main,
#     )
#     try:
#         await bot.send_message(
#             chat_id=ADMIN_ID,
#             text=f"Повідомлення від користувача {message.from_user.url}:\n\n{message.md_text}  \n\nБуло надіслано в З'вязок",
#         )

#     except Exception as e:
#         await bot.send_message(
#             chat_id=ADMIN_ID,
#             text=f"Помилка при відправці користувачу {message.from_user.url}: {e}",
#         )