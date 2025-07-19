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
    parts = name.strip().split()

    if len(parts) < 2:
        return "Помилка генерації посилання: Ім'я повинно складатися з принаймні двох слів"

    surname = parts[0]
    initials = []

    # Витягуємо перші літери або ініціали з крапками
    for part in parts[1:]:
        cleaned = part.strip(".")
        if cleaned:
            initials.append(cleaned[0])

    if not initials:
        return f"https://abit-poisk.org.ua/#search-{surname}"

    initials_str = '+'.join([surname] + initials)
    return f"https://abit-poisk.org.ua/#search-{initials_str}"
