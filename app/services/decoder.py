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
# along with this program.  If not, see <https://www.gnu.org/licenses/>

statuses = {
    "1": "Заява надійшла з сайту",
    "2": "Потребує уточнення",
    "3": "Скасовано вступником",
    "4": "Скасовано (втрата пріор.)",
    "5": "Зареєстровано",
    "6": "Допущено",
    "7": "Відмова",
    "8": "Скасовано ЗО",
    "9": "Рекомендовано (бюджет)",
    "10": "Відхилено (бюджет)",
    "11": "Допущено (контракт)",
    "12": "Рекомендовано (контракт)",
    "13": "Відхилено (контракт)",
    "14": "До наказу",
    "15": "Відраховано",
    "16": "Деактивовано (зарах. на бюджет)",
    "0": "Зареєстровано",
}

rec_types = {
    "-1": "Не реком. за жодним пріор.",
    "1": "На загальних умовах",
    "2": "За результатами співбесіди",
    "11": "За квотою 1",
    "12": "За квотою 2",
    "13": "За квотою 3",
    "20": "За квотою для іноземців",
}

# r[1] — № заяви
# r[2] — пріоритет
# r[3] — статус (із `statuses`)
# r[4] — ПІБ
# r[5] — конкурсний бал
# r[6–8] — квоти
# r[9–13] — коефіцієнти
# r[17] — тип (1=бюджет, 2=контракт)


async def decoder(tg_id: int, data: dict):
    pass
    # TODO Дописати декодер, щоб з бази витягував данні і повертав нормально оброблений
