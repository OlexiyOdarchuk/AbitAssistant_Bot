from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.services.mailing as mail
from app.states import States as st

router = Router()

@router.message(F.text == "📣Розсилка!")
async def mailing(message: Message, state: FSMContext):
    await mail.mailing(message, state)


@router.message(st.get_mailing, F.text)
async def get_mailing_text(message: Message, state: FSMContext):
    await mail.get_mailing_text(message, state)


@router.message(st.init_mailing, F.text == "Відправити розсилку📣")
async def init(message: Message, state: FSMContext):
    await mail.init(message, state)
