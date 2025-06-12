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

from app.database.models import async_session
from app.database.models import User, UserData
from sqlalchemy import select, delete, func, desc
from typing import List

async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_users() -> List[int]:
    async with async_session() as session:
        result = await session.execute(select(User.tg_id))
        return result.scalars().all()

async def set_user_data(
    tg_id: int,
    new_user_data: List[dict]  # кожен dict містить дані абітурієнтів
) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise Exception("User not found")

        # Видаляє всі існуючі записи user_data для цього користувача
        await session.execute(delete(UserData).where(UserData.user_tg_id == tg_id))

        # Додає всі нові записи
        user_data_objects = [
            UserData(
                user_tg_id=tg_id,
                name=item['name'],
                status=item.get('status'),
                priority=item['priority'],
                score=item.get('score'),
                detail=item.get('detail'),
                coefficient=item.get('coefficient'),
                quota=item.get('quota'),
                link=item['link'],
                competitor=item['competitor']
            )
            for item in new_user_data
        ]

        session.add_all(user_data_objects)
        await session.commit()

async def get_user_data(tg_id: int) -> List[UserData]:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise Exception("User not found")
        result = await session.scalars(select(UserData).where(UserData.user_tg_id == tg_id))
        return result.all()

async def clear_user_data(tg_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(UserData).where(UserData.user_tg_id == tg_id))
        await session.commit()

async def update_user_activates(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise Exception("User not found")
        user.activates = (user.activates or 0) + 1
        await session.commit()

async def update_user_right_activates(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise Exception("User not found")
        user.right_activates = (user.right_activates or 0) + 1
        await session.commit()

async def get_user_count() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(User))
        return result.scalar_one()

async def get_total_activates() -> dict[str, int]:
    async with async_session() as session:
        result = await session.execute(
            select(func.coalesce(func.sum(User.activates), 0), func.coalesce(func.sum(User.right_activates), 0))
        )
        activates_sum, right_activates_sum = result.one()
        return {
            "total_activates": activates_sum,
            "total_right_activates": right_activates_sum
        }

async def get_top_user() -> dict | None:
    async with async_session() as session:
        result = await session.execute(
            select(User.tg_id, User.activates)
            .order_by(desc(User.activates))
            .limit(1)
        )
        top = result.first()
        if top is None:
            return None
        tg_id, activates = top
        return {"tg_id": tg_id, "activates": activates or 0}
