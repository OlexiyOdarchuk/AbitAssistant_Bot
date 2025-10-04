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

import os
import sys
import asyncio
import asyncpg
from aiogram import Dispatcher
from app.services.logger import setup_logger, log_system_event, log_error

if not os.path.exists("config.py"):
    print(
        "\nФайл config.py не знайдено!\n"
        "Будь ласка, скопіюйте config.example.py у config.py та заповніть необхідні значення.\n"
        "Команда для Linux/macOS:\n"
        "  cp config.example.py config.py\n\n"
        "Команда для Windows:\n"
        "  copy config.example.py config.py\n"
    )
    sys.exit(1)

from config import bot, DATABASE_URL
from app.handlers import setup_routers
from app.database.models import async_main


dp = Dispatcher()


async def wait_for_postgres(dsn: str, timeout: int = 30):
    dsn_clean = dsn.replace(
        "+asyncpg", ""
    )  # asyncpg.connect не розуміє префікс SQLAlchemy
    for i in range(timeout):
        try:
            conn = await asyncpg.connect(dsn_clean)
            await conn.close()
            log_system_event("PostgreSQL is ready!")
            return
        except Exception as e:
            log_system_event("Waiting for PostgreSQL", str(e))
            await asyncio.sleep(1)
    raise TimeoutError("PostgreSQL did not become available in time.")


async def main():
    try:
        log_system_event("Starting AbitAssistant bot")
        await wait_for_postgres(DATABASE_URL)
        await async_main()
        setup_routers(dp)
        log_system_event("Bot started successfully")
        await dp.start_polling(bot)
    except Exception as e:
        log_error(e, "Error in main function")
        raise


if __name__ == "__main__":
    # Налаштування логування
    logger = setup_logger()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_system_event("Bot stopped by user")
        print("Exit")
    except Exception as e:
        log_error(e, "Fatal error in bot")
        print(f"Fatal error: {e}")
