from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.services.support as sup
from app.states import States as st

router = Router()

@router.message(F.text == "👤Зв'язок з адміністрацією👤")
async def support(message: Message, state: FSMContext):
    await sup.support(message, state)

@router.message(st.get_support, F.text)
async def get_support_text(message: Message, state: FSMContext):
    await sup.get_support_text(message, state)

@router.message(F.text)
async def forward(message: Message, state: FSMContext):
    await sup.forward(message, state)
