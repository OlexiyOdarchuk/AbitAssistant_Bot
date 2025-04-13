import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
import app.database.requests as rq
import app.keyboards as kb
import app.services.filter as fltr
import app.services.mailing as mail
import app.services.support as sup
import app.services.applicants_len as applicantlen
from app.states import States as st
from collections import defaultdict

user_score = defaultdict(dict)
router = Router()

@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id == ADMIN_ID:
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
    if message.from_user.id == ADMIN_ID:
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
    await mail.mailing(message, state)


@router.message(st.get_mailing, F.text)
async def get_mailing_text(message: Message, state: FSMContext):
    await mail.get_mailing_text(message, state)


@router.message(st.init_mailing, F.text == "Відправити розсилку📣")
async def init(message: Message, state: FSMContext):
    await mail.init(message, state)


@router.message(F.text == "👤Зв'язок з адміністрацією👤")
async def support(message: Message, state: FSMContext):
    await sup.support(message, state)

@router.message(st.get_support, F.text)
async def get_support_text(message: Message, state: FSMContext):
    await sup.get_support_text(message, state)

@router.message(F.text == "📝Почати відсіювання!📝")
async def start_filter(message: Message, state: FSMContext):
    await message.answer("Введіть свій середній рейтинговий бал на вибрану для фільтрації спеціальність:\n\
        Подивитися коефіцієнти можна на сайті https://www.education.ua/vstup/weighting-coefficients/\
\n\nА порахувати конкурсний бал на сайті: https://osvita.ua/consultations/konkurs-ball/", reply_markup=kb.return_back)
    await state.set_state(st.get_bal)

@router.message(st.get_bal, F.text)
async def get_bal(message: Message, state: FSMContext):
    try:
        if float(message.text) >= 100.000 and float(message.text) <=200.000:
            user_score[message.from_user.id]['score'] = message.text
            await state.set_state(st.get_link)
            await message.answer("Супер! Тепер відправте посилання на освітню програму з сайту vstup.osvita, наприклад:\n'https://vstup.osvita.ua/y2024/r27/41/1352329/'")
        else:
            await message.answer('Ваш бал повинен бути в межах від 100 до 200')
    except ValueError:
        await message.answer("Будь ласка, введіть число в межах від 100 до 200")

@router.message(st.get_link, F.text)
async def get_link(message: Message, state: FSMContext):
    try:
        if message.text.startswith('https://vstup.osvita.ua'):
            await state.set_state(st.choice_list)
            # await fltr.filter_applicants(message.from_user.id, user_score)
            await message.answer("Сканування почалося. Це займе деякий час")
            await asyncio.sleep(3)
            await message.answer("Зачекайте ще декілька секунд...")
            await asyncio.sleep(7)
            await message.answer("Ще трохи...")
            await asyncio.sleep(7)
            await message.answer("Майже готово...")
            await asyncio.sleep(7)
            await message.answer("Останні штрихи...")
            await asyncio.sleep(3)
            how_all_applicant = await applicantlen.all_applicant_len(message.from_user.id)
            how_competitor_applicant = await applicantlen.competitors_applicant_len(message.from_user.id)
            await message.answer(f"Готово!\nНа цю освітню програму наразі подано {how_all_applicant}, але з усіх цих людей конкуренцію вам складають тільки {how_competitor_applicant}\
\nМожете дізнатися більше, використовуючи кнопки нище, або поверніться до головного меню, щоб перевірити інші освітні програми!", reply_markup=kb.applicant_stat)


        else:
            await message.answer("Посилання повинно починатися з 'https://vstup.osvita.ua' та бути коректним")
    except ValueError:
        await message.answer("Будь ласка, введіть посилання на освітню програму")

@router.callback_query(StateFilter(st.view_all, st.view_competitors), F.data == "applicant_back_to_stat")
async def back_to_stat(callback: CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(st.choice_list)
    how_all_applicant = await applicantlen.all_applicant_len(callback.from_user.id)
    how_competitor_applicant = await applicantlen.competitors_applicant_len(callback.from_user.id)
    await callback.message.answer(f"Повернено!\nНа цю освітню програму наразі подано {how_all_applicant}, але з усіх цих людей конкуренцію вам складають тільки {how_competitor_applicant}\
\nМожете дізнатися більше, використовуючи кнопки нище, або поверніться до головного меню, щоб перевірити інші освітні програми!", reply_markup=kb.applicant_stat)

@router.callback_query(st.choice_list, F.data == "view_applicant_all")
async def view_applicant_all(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.view_all)
    keyboard = await kb.builder_applicant_all(callback.from_user.id, 1)
    await callback.message.edit_text("Всі заявки", reply_markup=keyboard)

@router.callback_query(st.view_all, F.data.startswith('applicant_page_'))
async def change_page_all(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    keyboard = await kb.builder_applicant_all(callback.from_user.id, page)
    await callback.message.edit_text("Осьо", reply_markup=keyboard)

@router.callback_query(st.choice_list, F.data == "view_applicant_competitors")
async def view_applicant_competitors(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.view_competitors)
    keyboard = await kb.builder_applicant_competitors(callback.from_user.id, user_score[callback.from_user.id]['score'], 1)
    await callback.message.edit_text("Всі заявки", reply_markup=keyboard)

@router.callback_query(st.view_competitors, F.data.startswith('competitors_page_'))
async def change_page_competitors(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    keyboard = await kb.builder_applicant_competitors(callback.from_user.id, user_score[callback.from_user.id]['score'], page)
    await callback.message.edit_text("Осьо", reply_markup=keyboard)

@router.callback_query(StateFilter(st.view_all, st.view_competitors), F.data.startswith('applicant_'))
async def all_info(callback: CallbackQuery):
    data = await rq.get_user_data(callback.from_user.id)
    applicant_id = int(callback.data.split('_')[-1])
    applicants = [applicant for applicant in data if applicant.user_tg_id == callback.from_user.id]
    for applicant in applicants:
        if applicant.id == applicant_id:
            await callback.message.answer(
f"""Повна інформація про абітурієнта:

ПІП: {applicant.name}
Статус заяви: {applicant.status}
Приорітет на освітню програму: {applicant.priority}
Коефіцієнтний бал на спеціальність: {applicant.score}

Бали НМТ:
 {applicant.detail}

Коефіцієнт: {applicant.coefficient}
Квота: {applicant.quota}
Конкурентність: {bool(applicant.competitor)}
Посилання на абіт-пошук:
{applicant.link}""")


@router.message(F.text)
async def forward(message: Message, state: FSMContext):
    await sup.forward(message, state)
