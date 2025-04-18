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

async def generate_link(name: str) -> str:
    """Асинхронно генерує посилання на абітурієнта на сайті abit-poisk.org

    Args:
        name (str): Прізвище і ініціали (або ім'я і по-батькові) абітурієнта

    Returns:
        str: Посилання на сайт abit-poisk.org
    """
    await asyncio.sleep(0)
    parts = name.split()
    if len(parts) < 2:
        return "Помилка: Неправильно введене ім'я!!!"
    surname = parts[0]
    first_initial = parts[1][0]
    if len(parts) > 2:
        middle_initial = parts[2][0]
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}+{middle_initial}"
    elif len(parts) == 2:
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}"
    else:
        return ValueError
