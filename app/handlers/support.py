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

import app.services.support as sup
from app.states import States as st

router = Router()

@router.message(F.text == "👤 Зв'язок з адміністрацією 👤")
async def support(message: Message, state: FSMContext):
    await sup.support(message, state)

@router.message(st.get_support, F.text == "📤 Відправити")
async def send_all_to_admin(message: Message, state: FSMContext):
    await sup.send_all_to_admin(message, state)

@router.message(st.get_support)
async def collect_messages(message: Message, state: FSMContext):
    await sup.collect_user_message(message, state)

@router.message(F.text)
async def forward_reply_from_admin(message: Message, state: FSMContext):
    await sup.forward(message, state)
