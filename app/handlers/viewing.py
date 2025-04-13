from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

import app.keyboards as kb
import app.database.requests as rq
import app.services.applicants_len as applicantlen
from app.states import States as st
from app.handlers.filtering import user_score

router = Router()

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
