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

from sqlalchemy import BigInteger, MetaData, Index, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql.schema import ForeignKey
from typing import Optional, List
from config import DATABASE_URL

engine = create_async_engine(url=DATABASE_URL)
metadata = MetaData()
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    user_data: Mapped[List["UserData"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    activates: Mapped[int] = mapped_column(Integer, default=0)
    right_activates: Mapped[int] = mapped_column(Integer, default=0)

class UserData(Base):
    __tablename__ = "user_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    priority: Mapped[int] = mapped_column(Integer)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    coefficient: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    quota: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    link: Mapped[str] = mapped_column(String)
    competitor: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship(back_populates="user_data")

    __table_args__ = (
        Index('user_data_index', 'user_tg_id', 'status', 'coefficient', 'quota', 'score', 'competitor'),
    )

    def as_dict(self):
        return {
            "id": self.id,
            "tg_id": self.user_tg_id,
            "name": self.name,
            "status": self.status,
            "coefficient": self.coefficient,
            "quota": self.quota,
            "score": self.score,
            "competitor": self.competitor,
        }


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
