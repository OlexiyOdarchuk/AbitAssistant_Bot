import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, bot
import app.database.requests as rq
from app.services.parser import parser
from app.services.generate_link import generate_link
import app.keyboards as kb
from app.states import States as st
import app.services.mailing as mail
import app.services.support as sup


async def parse(message:Message, state:FSMContext):
    await parser(message.text, message.from_user.id)
