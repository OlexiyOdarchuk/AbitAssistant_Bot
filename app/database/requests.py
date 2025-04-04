from app.database.models import async_session, metadata, engine
from app.database.models import User
from sqlalchemy import Column, Integer, String, Table, select

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_users():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id))
        return result.scalars().all()

async def create_user_table(tg_id):
    table_name = f"user_{tg_id}"
    
    user_table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('priority', Integer),
        Column('status', String),
        Column('bal', Integer),
        Column('type', String),
        Column('link', String),
    )
    metadata.create_all(engine, tables=[user_table])
    return user_table