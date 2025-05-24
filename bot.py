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
import logging
import asyncpg
from aiogram import Dispatcher

from config import bot, DATABASE_URL
from app.handlers import setup_routers
from app.database.models import async_main


dp = Dispatcher()


async def wait_for_postgres(dsn: str, timeout: int = 30):
    dsn_clean = dsn.replace("+asyncpg", "")  # asyncpg.connect не розуміє префікс SQLAlchemy
    for i in range(timeout):
        try:
            conn = await asyncpg.connect(dsn_clean)
            await conn.close()
            logging.info("PostgreSQL is ready!")
            return
        except Exception as e:
            logging.warning(f"Waiting for PostgreSQL... {e}")
            await asyncio.sleep(1)
    raise TimeoutError("PostgreSQL did not become available in time.")


async def main():
    await wait_for_postgres(DATABASE_URL)
    await async_main()
    setup_routers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
