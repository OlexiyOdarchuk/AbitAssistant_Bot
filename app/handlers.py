from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
from app.services.parser import parser
from app.services.generate_link import generate_link

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer("СТАРТОВЕ ПОВІДОМЛЕННЯ ДОПИСАТИ НЕ ЗАБУДЬ")