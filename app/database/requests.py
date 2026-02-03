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
from app.database.models import User, CompetitorCache, SavedList, URLCache
from sqlalchemy import select, func, desc, delete
from sqlalchemy.dialects.postgresql import insert
from typing import List, Optional
from datetime import datetime, timedelta


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


async def update_user_activates(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            # Якщо користувача ще немає, створюємо
            user = User(tg_id=tg_id, activates=1)
            session.add(user)
        else:
            user.activates = (user.activates or 0) + 1
        await session.commit()


async def update_user_right_activates(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
             user = User(tg_id=tg_id, right_activates=1)
             session.add(user)
        else:
            user.right_activates = (user.right_activates or 0) + 1
        await session.commit()


async def get_user_count() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(User))
        return result.scalar_one()


async def get_total_activates() -> dict[str, int]:
    async with async_session() as session:
        result = await session.execute(
            select(
                func.coalesce(func.sum(User.activates), 0),
                func.coalesce(func.sum(User.right_activates), 0),
            )
        )
        activates_sum, right_activates_sum = result.one()
        return {
            "total_activates": activates_sum,
            "total_right_activates": right_activates_sum,
        }


async def get_top_user() -> dict | None:
    async with async_session() as session:
        result = await session.execute(
            select(User.tg_id, User.activates).order_by(desc(User.activates)).limit(1)
        )
        top = result.first()
        if top is None:
            return None
        tg_id, activates = top
        return {"tg_id": tg_id, "activates": activates or 0}


# --- Робота з даними користувача (НМТ та Налаштування) ---

async def get_user_nmt(tg_id: int) -> dict:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return {}
        return user.nmt_scores or {}


async def set_user_nmt(tg_id: int, nmt_scores: dict) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
             user = User(tg_id=tg_id)
             session.add(user)
        
        user.nmt_scores = nmt_scores
        await session.commit()


async def get_user_settings(tg_id: int) -> dict:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return {}
        return user.settings or {}


async def set_user_settings(tg_id: int, settings: dict) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
             user = User(tg_id=tg_id)
             session.add(user)
        
        user.settings = settings
        await session.commit()


# --- Робота зі збереженими списками ---

async def save_specialty_list(tg_id: int, name: str, url: str, data: dict) -> int:
    """Зберігає список і повертає його ID"""
    async with async_session() as session:
        saved_list = SavedList(
            user_tg_id=tg_id,
            name=name,
            url=url,
            data=data
        )
        session.add(saved_list)
        await session.commit()
        return saved_list.id


async def get_saved_lists(tg_id: int) -> List[SavedList]:
    async with async_session() as session:
        result = await session.scalars(
            select(SavedList)
            .where(SavedList.user_tg_id == tg_id)
            .order_by(desc(SavedList.created_at))
        )
        return result.all()


async def get_saved_list(list_id: int) -> Optional[SavedList]:
    async with async_session() as session:
        return await session.scalar(select(SavedList).where(SavedList.id == list_id))


async def delete_saved_list(list_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(SavedList).where(SavedList.id == list_id))
        await session.commit()


# --- Робота з кешем конкурентів ---

async def get_cached_competitor(name: str, cache_validity_seconds: int = 86400) -> Optional[List[dict]]:
    """
    Отримує дані конкурента з кешу, якщо вони не застаріли.
    Default validity: 24 години (86400 с).
    """
    async with async_session() as session:
        competitor = await session.scalar(select(CompetitorCache).where(CompetitorCache.name == name))
        
        if not competitor:
            return None
            
        now = datetime.now()
        # Спрощений варіант: якщо updated_at + valid < now -> застаріло
        if competitor.updated_at.replace(tzinfo=None) + timedelta(seconds=cache_validity_seconds) < now:
            return None
            
        return competitor.data


async def cache_competitor(name: str, data: List[dict]) -> None:
    """
    Зберігає або оновлює дані конкурента в кеші.
    Використовує UPSERT (on conflict do update).
    """
    async with async_session() as session:
        stmt = insert(CompetitorCache).values(name=name, data=data, updated_at=datetime.now())
        stmt = stmt.on_conflict_do_update(
            index_elements=['name'],
            set_={'data': stmt.excluded.data, 'updated_at': datetime.now()}
        )
        await session.execute(stmt)
        await session.commit()


# --- Глобальний кеш URL ---

async def get_cached_url(url: str, validity_minutes: int = 10) -> Optional[dict]:
    """
    Отримує розпарсені дані URL з кешу, якщо вони свіжі.
    Default validity: 10 хвилин.
    """
    async with async_session() as session:
        cached = await session.scalar(select(URLCache).where(URLCache.url == url))
        
        if not cached:
            return None
            
        now = datetime.now()
        # Check expiration
        if cached.updated_at.replace(tzinfo=None) + timedelta(minutes=validity_minutes) < now:
            return None
            
        return cached.data


async def cache_url(url: str, data: dict) -> None:
    """
    Зберігає розпарсені дані URL в кеш.
    """
    async with async_session() as session:
        stmt = insert(URLCache).values(url=url, data=data, updated_at=datetime.now())
        stmt = stmt.on_conflict_do_update(
            index_elements=['url'],
            set_={'data': stmt.excluded.data, 'updated_at': datetime.now()}
        )
        await session.execute(stmt)
        await session.commit()
