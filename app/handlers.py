import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import app.database.requests as rq
from app.services.parser import parser
from app.services.generate_link import generate_link
import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id == 1433760480:
        await message.answer("О, ку!\nНа менюшку, може вона тобі треба)", reply_markup=kb.admin_main) 
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
        await message.answer("Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇", reply_markup=kb.user_main)


@router.message(F.text == '❌ До головного меню')
async def return_back(message: Message):
            await message.answer("Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇", reply_markup=kb.user_main)
            

@router.message(F.text == '💸Донат💸')
async def donate(message: Message):
    await message.answer("""Сюди ви можете задонатити мені на новий ноутбук для навчання та програмування, буду дуже вдячний 🥰

🎯 Ціль: 70 000 ₴

🔗Посилання на банку
https://send.monobank.ua/jar/23E3WYNesG

💳Номер картки банки
5375 4112 0596 9640
                        """, reply_markup=kb.return_back)
    
    
@router.message(F.text == "📑Про нас📑")
async def about_us(message: Message):
    await message.answer("Хтось взагалі натискає на цю кнопку?...", reply_markup=kb.remove_keyboard)
    await asyncio.sleep(2)
    await message.answer('Ну раз натиснули, значить цікаво)))')
    await asyncio.sleep(1)
    await message.answer('Тут тіпа шось написав щось дуже важне прям огого тут я допишу коли небудь шось про себе і взагалі цю програму, бо щас лєнь придумувати.\
\nВзагалі я бідний студент, так що давайте якось задонатьте, чи що ', reply_markup=kb.about_us)