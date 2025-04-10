from app.database.models import async_session, metadata, engine
from app.database.models import User, UserData
from sqlalchemy import Column, Integer, String, Table, select

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def create_user_data_table():
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
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def get_users():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id))
        return result.scalars().all()

async def set_user_data(tg_id, name, status, priority, score, detail, coefficient, quota, link, competitor):
    await create_user_data_table()
    async with async_session() as session:
        # Перевіряємо, чи існує запис користувача
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
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

async def get_user_data(tg_id):
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
