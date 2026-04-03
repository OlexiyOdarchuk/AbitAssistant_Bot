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

from sqlalchemy import BigInteger, MetaData, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql import func
from typing import Optional, Dict, List
from config import DATABASE_URL
from datetime import datetime

engine = create_async_engine(url=DATABASE_URL)
metadata = MetaData()
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    # Зберігаємо бали користувача: {"Ukr": 170, "Math": 180, ...}
    nmt_scores: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    # Налаштування: {"quotas": ["kv1"], "region_coef": true, "creative_score_prediction": 150}
    settings: Mapped[Optional[Dict]] = mapped_column(JSON, default={})

    # Статистика використання
    activates: Mapped[int] = mapped_column(Integer, default=0)
    right_activates: Mapped[int] = mapped_column(Integer, default=0)

    saved_lists: Mapped[List["SavedList"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SavedList(Base):
    """
    Збережені користувачем списки (спеціальності).
    Зберігають snapshot даних на момент аналізу.
    """

    __tablename__ = "saved_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String)  # Назва спеціальності/ВНЗ
    url: Mapped[str] = mapped_column(String)
    data: Mapped[Dict] = mapped_column(
        JSON
    )  # Повний JSON оброблених даних (competitors, chances etc.)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="saved_lists")


class CompetitorCache(Base):
    """
    Кеш для зберігання інформації про конкурентів.
    """

    __tablename__ = "competitor_cache"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    data: Mapped[Dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class URLCache(Base):
    """
    Глобальний кеш для розпарсених сторінок університетів.
    Дозволяє не парсити одну й ту ж сторінку 100 разів для різних юзерів.
    """

    __tablename__ = "url_cache"

    url: Mapped[str] = mapped_column(String, primary_key=True)
    data: Mapped[Dict] = mapped_column(JSON)  # Результат parser()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
