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

from app.database.requests import get_nmt

# nmt = {
#     "Українська мова": 145.3,
#     "Математика": 154.3,
#     "Історія України": 144.0,
#     "Українська література": 0,
#     "Іноземна мова": 0,
#     "Біологія": 0,
#     "Географія": 0,
#     "Фізика": 154.3,
#     "Хімія": 0,
#     "Мотиваційний лист": 0.0,
# }


def calculate_rating_store(data: dict, tg_id: int):
    nmt = get_nmt(tg_id)

    # TODO: Дописати калькулятор


def filter_data(data: dict, tg_id: int) -> dict:
    """Функція приймає телеграм id, дані які треба профільтрувати і фільтрує їх за алгоритмом. Повертає результат фільтрації"""

    # TODO: Дописати фільтр
