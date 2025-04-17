from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.services.support as sup
from app.states import States as st

router = Router()

@router.message(F.text == "👤Зв'язок з адміністрацією👤")
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
