import asyncio
import time

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, bot
import app.database.requests as rq
from app.services.parser import parser
from app.services.generate_link import generate_link
import app.keyboards as kb
from app.states import States as st

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "О, ку!\nНа менюшку, може вона тобі треба)", reply_markup=kb.admin_main
        )
    else:
        await rq.set_user(message.from_user.id)
        await message.answer("""Вітаю в боті для перевірки конкурекції! 👋
                                 
Тут ми реалізували фільтрацію конкурентів для абітурієнтів(тобто майбуніх студентів😋),
щоб ви не витрачали свій дорогоцінний час на однотипну роботу, яка, як правило, добре автоматизується!
Ця програма буде корисна для тих,
хто тільки подає заявки до університетів!

P.s. Та має не 200 з усіх предметів НМТ..
Для вас взагалі конкуренції не існує🫣
                                
                                😉Успіхів!✊
                                """)
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main,
        )


@router.message(F.text == "❌ До головного меню")
async def return_back(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.admin_main,
        )
    else:
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.user_main,
        )


@router.message(F.text == "💸Донат💸")
async def donate(message: Message):
    await message.answer(
        """Сюди ви можете задонатити мені на новий ноутбук для навчання та програмування, буду дуже вдячний 🥰

🎯 Ціль: 70 000 ₴

🔗Посилання на банку
https://send.monobank.ua/jar/23E3WYNesG

💳Номер картки банки
5375 4112 0596 9640
                        """,
        reply_markup=kb.return_back,
    )


@router.message(F.text == "📑Про нас📑")
async def about_us(message: Message):
    await message.answer(
        "Хтось взагалі натискає на цю кнопку?...", reply_markup=kb.remove_keyboard
    )
    await asyncio.sleep(2)
    await message.answer("Ну раз натиснули, значить цікаво)))")
    await asyncio.sleep(1)
    await message.answer(
        "Тут тіпа шось написав щось дуже важне прям огого тут я допишу коли-небудь шось про себе і взагалі цю програму, бо щас лєнь придумувати.\
\nВзагалі я бідний студент, так що давайте якось задонатьте, чи що ",
        reply_markup=kb.about_us,
    )


@router.message(F.text == "📣Розсилка!")
async def mailing(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
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


@router.message(st.get_mailing, F.text)
async def get_mailing_text(message: Message, state: FSMContext):
    await state.update_data(mailing_text=message.md_text)
    await message.answer("Текст прийнято, повідомлення виглядає ось так:")
    data = await state.get_data()
    mailing_text = data.get("mailing_text", "Текст не знайдено!!!")
    await message.answer(
        f"📣Повідомлення з розсилки: \n\n{mailing_text}", reply_markup=kb.mailing
    )
    await state.set_state(st.init_mailing)


@router.message(st.init_mailing, F.text == "Відправити розсилку📣")
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
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Помилка при відправці користувачу tg://user?id={user}: {e}",
            )

    elapsed_time = round(time.time() - start_time, 2)

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Розсилка завершена! \nВідправлено {sent_count} повідомлень за {elapsed_time} секунд.",
        reply_markup=kb.admin_main,
    )
    await state.set_state(None)


@router.message(F.text == "👤Зв'язок з адміністрацією👤")
async def support(message: Message, state: FSMContext):
    await message.answer(
        "Наступне повідомлення буде відправлено адміністрації, формулюйте його уважно:",
        reply_markup=kb.return_back,
    )
    await state.set_state(st.get_support)


@router.message(st.get_support, F.text)
async def get_support_text(message: Message, state: FSMContext):
    await message.answer(
        "Ваше повідомлення зареєстровано, дякую за відгук. \nВам дадуть відповідь найближчим часом."
    )
    await state.set_state(None)
    await message.answer(
        "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
        reply_markup=kb.user_main,
    )
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Повідомлення від користувача {message.from_user.url}:\n\n{message.md_text}  \n\nБуло надіслано в З'вязок",
        )

    except Exception as e:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Помилка при відправці користувачу {message.from_user.url}: {e}",
        )


@router.message(F.text)
async def forward(message: Message):
    if message.from_user.id != ADMIN_ID:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Повідомлення від користувача {message.from_user.url}:\n\n{message.md_text} \n\nБуло надіслано випадково",
        )