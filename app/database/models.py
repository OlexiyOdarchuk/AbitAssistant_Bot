from sqlalchemy import BigInteger, create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import app.database.requests as rq

engine = create_async_engine(url="sqlite+aiosqlite:///app/database/db.sqlite3")
metadata = MetaData()
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def insert_into_user_table(user_id, id, name, priority, status, bal, type, link):
    table = rq.create_user_table(user_id) 
    with engine.connect() as conn:
        conn.execute(table.insert().values(id=id, name=name, priority=priority, status=status, bal=bal, type=type, link=link))