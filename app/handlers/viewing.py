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

import re
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

import app.keyboards as kb
import app.database.requests as rq
import app.services.applicants_len as applicantlen
from app.states import States as st
from config import user_score

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
    await callback.message.edit_text("Всі буджетні заяви на дану освітню програму", reply_markup=keyboard)

@router.callback_query(st.view_all, F.data.startswith('applicant_page_'))
async def change_page_all(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    keyboard = await kb.builder_applicant_all(callback.from_user.id, page)
    await callback.message.edit_text("Натисніть на абітурієнта, щоб побачити повну інформацію\nНатисніть на кнопки керування, щоб пересуватися сторінками та на номер сторінки, щоб повернутися до попереднього меню", reply_markup=keyboard)

@router.callback_query(st.choice_list, F.data == "view_applicant_competitors")
async def view_applicant_competitors(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.view_competitors)
    keyboard = await kb.builder_applicant_competitors(callback.from_user.id, user_score[callback.from_user.id], 1)
    await callback.message.edit_text("Всі конкурентноспроможні заявки на дану освітню програму", reply_markup=keyboard)

@router.callback_query(st.view_competitors, F.data.startswith('competitors_page_'))
async def change_page_competitors(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    keyboard = await kb.builder_applicant_competitors(callback.from_user.id, user_score[callback.from_user.id], page)
    await callback.message.edit_text("Натисніть на абітурієнта, щоб побачити повну інформацію\nНатисніть на кнопки керування, щоб пересуватися сторінками та на номер сторінки, щоб повернутися до попереднього меню", reply_markup=keyboard)

@router.callback_query(StateFilter(st.view_all, st.view_competitors), F.data.startswith('applicant_'))
async def all_info(callback: CallbackQuery):
    await callback.answer()
    data = await rq.get_user_data(callback.from_user.id)
    applicant_id = int(callback.data.split('_')[-1])
    applicants = [applicant for applicant in data if applicant.user_tg_id == callback.from_user.id]
    for applicant in applicants:
        if applicant.id == applicant_id:
            display_quota = applicant.quota if applicant.quota else "-"
            display_coefficient = applicant.coefficient if applicant.coefficient else "-"
            formatted_detail = "-"
            if applicant.detail:
                formatted_detail = re.sub(r'([А-ЯІЇЄA-Zа-яіїєҐґ\s]+?)(\d{2,3})(?=[А-ЯІЇЄA-Z])', r'\1: \2\n', applicant.detail).strip() # ([А-ЯІЇЄA-Zа-яіїєҐґ\s]+?) - ловить назву, (\d{2,3}) - ловить число, (?=[А-ЯІЇЄA-Z]) - після числа повинно бути велика літера
            await callback.message.answer(
f"""Повна інформація про абітурієнта:

ПІП: {applicant.name}
Статус заяви: {applicant.status}
Пріоритет на освітню програму: {applicant.priority}
Коефіцієнтний бал на спеціальність: {applicant.score if applicant.score else '-'}

Бали НМТ:
{formatted_detail}

Коефіцієнт: {display_coefficient}
Квота: {display_quota}
Конкурентність: {'Конкурент' if applicant.competitor else 'Не конкурент'}
Посилання на абіт-пошук:
{applicant.link if applicant.link else '-'}
""")
