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

from sqlalchemy import select
from app.database.models import async_session, User
from typing import List
import logging

logger = logging.getLogger(__name__)

async def get_users_with_links(limit: int = 50) -> str:
    """Отримує список користувачів з посиланнями tg://user?id= для адміністраторів"""
    try:
        async with async_session() as session:
            query = select(User.tg_id).limit(limit)
            result = await session.execute(query)
            user_ids = result.scalars().all()

            if not user_ids:
                return "📋 **Список користувачів**\n\n❌ Користувачів не знайдено"

            result_text = "📋 **Список користувачів**\n\n"

            for i, tg_id in enumerate(user_ids, 1):
                result_text += f"{i}. tg://user?id={tg_id}\n"

            return result_text

    except Exception as e:
        logger.error(f"Error getting users with links: {e}")
        return "❌ Помилка отримання списку користувачів"
