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

import time
import json
import base64
from logger import log_parsing_action


def generate_abit_poisk_link(name: str, tg_id: int) -> str:
    """Асинхронно генерує посилання на абітурієнта на сайті abit-poisk.org

    Args:
        name (str): Прізвище і ініціали (або ім'я і по-батькові) абітурієнта
    Returns:
        str: Посилання на сайт abit-poisk.org
    """
    time.sleep(0)
    parts = name.strip().split()

    if len(parts) < 2:
        log_parsing_action(
            tg_id,
            "generate_abit_poisk_link failed",
            f"Помилка генерації посилання для {name}: замало слів",
        )
        return (
            "Помилка генерації посилання: Ім'я повинно складатися з принаймні двох слів"
        )

    surname = parts[0]
    initials = []

    # Витягуємо перші літери або ініціали з крапками
    for part in parts[1:]:
        cleaned = part.strip(".")
        if cleaned:
            initials.append(cleaned[0])

    log_parsing_action(tg_id, "generate_abit_poisk_link")

    if not initials:
        return f"https://abit-poisk.org.ua/#search-{surname}"

    initials_str = "+".join([surname] + initials)
    return f"https://abit-poisk.org.ua/#search-{initials_str}"


def btoa_py(js_obj: list) -> str:
    """
    Симулює JS btoa(JSON.stringify(obj))

    Args:
        js_obj (list): список словників з балами і коефіцієнтами
    Return:
        str: містить тільки ASCII (ключі та числа)
    """
    js_str = json.dumps(js_obj, separators=(",", ":"))  # мінімальні пробіли як у JS
    # перетворення у байти Latin1 (симуляція JS btoa)
    js_bytes = js_str.encode("latin1", errors="ignore")
    return base64.b64encode(js_bytes).decode("ascii")


def generate_calc_link(
    subjson: list, fxbal: float, eb: int, okr: int, tg_id: int
) -> str:
    """
    Генерує посилання на калькулятор для абітурієнта.

    Args:
        subjson: список словників з балами і коефіцієнтами
        fxbal: конкурсний бал (abit[5])
        eb: рівень освіти
        okr: тип навчання (як у JS)
    Returns:
        str: Посилання на калькулятор
    """
    urlcalc = "https://osvita.ua/consultations/konkurs-ball/?subjson="

    if eb == 40 and okr not in (4, 9):
        subjson_b64 = btoa_py(subjson)
        log_parsing_action(tg_id, "generate_calc_link")
        return f"{urlcalc}{subjson_b64}&rbal={fxbal:.3f}"
    log_parsing_action(tg_id, "generate_calc_link failed")
    return "Не вдалося згенерувати посилання на калькулятор"
