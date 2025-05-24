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
