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

from app.database.models import async_session, metadata, engine
from app.database.models import User, UserData
from sqlalchemy import Column, Integer, String, Table, select, delete
from typing import List

async def set_user(tg_id) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def create_user_data_table() -> None:
    """Створює таблицю UserData."""
    user_data_table = Table(
        'user__data', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_tg_id', Integer, nullable=False),
        Column('name', String, nullable=False),
        Column('status', String, nullable=True),
        Column('priority', Integer, nullable=False),
        Column('score', Integer, nullable=True),
        Column('detail', String, nullable=True),
        Column('coefficient', String, nullable=True),
        Column('quota', String, nullable=True),
        Column('link', String, nullable=False),
        Column('competitor', Integer, nullable=False),
        extend_existing=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def get_users():
    """Повертає список користувачів з таблиці User."""
    async with async_session() as session:
        result = await session.execute(select(User.tg_id))
        return result.scalars().all()

async def set_user_data(tg_id: int, name: str, status: str, priority: int, score: float, detail: str, coefficient: str, quota: str, link: str, competitor: bool) -> None:
    """Встановлює дані користувача в таблицю UserData."""
    await create_user_data_table()
    async with async_session() as session:
        # Перевіряємо, чи існує запис користувача
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            # Видаляємо попередні дані користувача з таблиці UserData
            # Додаємо дані для користувача в таблицю UserData
            user_data = UserData(
                user_tg_id=tg_id,
                name=name,
                status=status,
                priority=priority,
                score=score,
                detail=detail,
                coefficient=coefficient,
                quota=quota,
                link=link,
                competitor=competitor
            )
            session.add(user_data)
            await session.commit()
        else:
            # Якщо користувач не знайдений, можна повернути помилку чи створити його
            raise Exception("User not found")

async def get_user_data(tg_id: int) -> List[UserData]:
    """Повертає дані користувача з таблиці UserData."""
    async with async_session() as session:
        # Перевіряємо, чи існує запис користувача
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            # Отримуємо дані для користувача з таблиці UserData
            user_data_result = await session.scalars(select(UserData).where(UserData.user_tg_id == tg_id))
            user_data = user_data_result.all()
            return user_data
        else:
            raise Exception("User not found")

async def clear_user_data(tg_id: int) -> None:
    """Видаляє всі записи користувача перед новим парсингом."""
    async with async_session() as session:
        await session.execute(
            delete(UserData).where(UserData.user_tg_id == tg_id)
        )
        await session.commit()
