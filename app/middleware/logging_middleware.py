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

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.services.logger import log_user_action, log_admin_action, log_error
from config import ADMIN_ID

class LoggingMiddleware(BaseMiddleware):
    """Middleware для автоматичного логування дій користувачів"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        try:
            # Логується вхідне повідомлення
            if isinstance(event, Message):
                user_id = event.from_user.id
                username = event.from_user.username
                action = f"Sent message: {event.text[:50]}" if event.text else "Sent non-text message"

                if user_id in ADMIN_ID:
                    log_admin_action(user_id, action)
                else:
                    log_user_action(user_id, username, action)

            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                username = event.from_user.username
                action = f"Callback: {event.data}"

                if user_id in ADMIN_ID:
                    log_admin_action(user_id, action)
                else:
                    log_user_action(user_id, username, action)

            # Обробник
            return await handler(event, data)

        except Exception as e:
            # Логується помилка
            user_id = event.from_user.id if hasattr(event, 'from_user') else 'unknown'
            log_error(e, f"Error in handler for user {user_id}")
            raise
