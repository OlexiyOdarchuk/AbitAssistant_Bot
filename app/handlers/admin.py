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

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.services.mailing as mail
from app.states import States as st
import app.services.stats as stats

router = Router()

@router.message(F.text == "📣Розсилка!")
async def mailing(message: Message, state: FSMContext):
    await mail.mailing(message, state)


@router.message(st.get_mailing)
async def get_mailing_text(message: Message, state: FSMContext):
    await mail.get_mailing_text(message, state)


@router.message(st.init_mailing, F.text == "Відправити розсилку📣")
async def init(message: Message, state: FSMContext):
    await mail.init(message, state)

@router.message(F.text == "📊Статистика!")
async def statistics(message: Message):
    await message.answer(await stats.admin_statistics())
