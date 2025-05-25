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
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.keyboards as kb
from config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id in ADMIN_ID:
        await rq.set_user(message.from_user.id)
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
async def return_back(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await state.set_state(None)
        await message.answer(
            "Ви в головному меню.\nДля координації по боту скористайтеся кнопками нижче👇",
            reply_markup=kb.admin_main,
        )
    else:
        await state.set_state(None)
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
        "Захотілося почитати історію проєкту?)", reply_markup=kb.remove_keyboard
    )
    await asyncio.sleep(3)
    await message.answer("Тоді тримай😊")
    await message.answer(
        """Вітаю! Я студент фахового коледжу інформаційних технологій Націольного Університету "Львівська Політехніка", першокурсник.\
Ця програма створена 1 людиною, що тільки починає створювати великі проєкти, тому не судіть суворо))

Робота несе з собою 2 мети.

Перша: Отримати досвід в написанні телеграм ботів, роботи з парсингом, базами данних та іними технологіями в програмуванні на Python.

Друга і основна: Допомгти випускникам отримати шанс на бюджет незалежно від їх балів і без лишньої мороки."""
    )
    await message.answer(
        """А тепер трішки про сам проєкт і його історію:

Почалося все ще в 2024 році, коли ми з товаришем вступали (Я в коледж після 9, а він в університет після 11).
Мій період подачі заяв почався раніше і я зі спокійнею душею подав документи, здав вступні екзамени і... Написав невеликий скрипт для того, щоб продивлюватися які взагалі в мене шанси на вступ.
А от коли почався його період подачі заяв, він скинув мені ось це відео: https://www.youtube.com/watch?v=m5YfI8_2ONo
І написав, що вже 2 години фільтрує тільки 3 спеціальність і він розуміє, що треба буде робити це ще раз завтра, і може ще не один день.
Оскільки ми обидва поступали на програмістів, я покликав його до себе і разом за 2 години ми написали повністю робочу програму в консолі, яка зчитує дані з txt файла, сортує і видає бажаний результат.
Пізніше ми дописали туди tkinter для гарного виводу данних, але все ж, це залишалася проблема - це локальна програма, яку потрібно запускати маючи пк і середовище розробки на ньому.
Звісно, найбільший недолік цієї прогами був у складному запуску, інтерфейсі і тому, що потрібно спочатку скопіювати дані з сайту, але не зважаючи на це, вона повністю працює і зараз, при бажанні ви можете завантажити її з репозиторію і спробувати запустити.👇
https://github.com/OlexiyOdarchuk/Competition-Check"""
    )
    await message.answer(
        """Отже. Програма була, але користуватися нею міг не кожен, тому я і вирішив дописати її в вигляді зручного телеграм бота.
Тут використовуються бази данних, парсери, драйвери браузерів телеграм API і ще купа всякого, а головне - вся програма є у відкритому доступі з відкритим вихідним кодом і росповсюджується під ліцензією GPLv3.
Це дозволяє кожному з вас подивитися її код, міняти його під себе та розповсюджувати далі з відкритим кодом. Весь технічний опис і код програми ви можете знайти в моєму репозиторії:
https://github.com/OlexiyOdarchuk/AbitAssistant_bot"""
    )
    await message.answer(
        """Буду чекати там всіх програмістів і з радістю прийму ваші пропозиції для покращень!

А ще, було б непогано, якби хтось скинув пару гривень як донат за пророблену роботу та на підтримку проєкту, бо сервери нині недешеві 👉👈""",
reply_markup=kb.about_us
    )
