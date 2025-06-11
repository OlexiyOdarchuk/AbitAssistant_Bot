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

import asyncio
import os
from aiogram import Bot

TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN" # API Token телеграм бота

# URL бази данних, вставте своє ім'я, пароль і назву бази даних, але щоб співпадало з docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://name:password@localhost:5432/name_db")

ADMIN_ID = [1234567890, 6587654321, 1122334455] # ID ваших Адміністраторів

# Семафор для обмеження кількості паралельних завдань, вписуйте сюди кількість, яку витримає сервер (не більше 3, бо не витримає selenium)
MULTITASK = asyncio.Semaphore(2)

bot = Bot(token=TELEGRAM_TOKEN)
