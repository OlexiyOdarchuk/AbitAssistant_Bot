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

from dataclasses import dataclass, asdict, field
import generate_link
from logger import log_parsing_action, log_error


@dataclass
class Abiturient:
    id: int = 0
    num: int = 0
    priority: int = 0
    status: str = ""
    name: str = ""
    bal: float = 0.0
    quota: str = ""
    coef: str = ""
    documents: str = ""
    rec_type: str = ""
    state_education: str = ""
    other_req: int = 0
    abit_link: str = ""
    calc_link: str = ""
    nmt_bals: dict = field(default_factory=dict)


class AbiturientDecoder:
    """Декодер для обробки даних абітурієнтів."""

    # Індекси полів у масиві abit
    ID = 0
    NUM = 1
    PRIORITY = 2
    STATUS = 3
    NAME = 4
    BAL = 5
    QUOTA1 = 6
    QUOTA2 = 7
    QUOTA3 = 8
    COEF_GK = 9
    COEF_SK = 10
    COEF_PCHK = 11
    COEF_OL = 12
    COEF_KR = 13
    DOCUMENTS = 14
    REC_TYPE = 15
    INTERVIEW = 16
    STATE_EDUCATION = 17
    OTHER_REQ = 18

    # Коди предметів
    ATTESTAT = 100
    GK = 109
    SK = 110
    PCHK = 111
    OL = 112
    RK = 120
    K4MAX = 140

    def __init__(self, data: dict, tg_id: int):
        """
        Ініціалізує декодер з даними.

        Args:
            data: Словник з даними абітурієнтів
            tg_id: Telegram ID користувача
        """
        self.tg_id = tg_id
        self.data = data.copy()

        # Загальні параметри
        self.statuses = self.data.get("statuses", {})
        self.rec_types = self.data.get("rec_types", {})
        self.requests_raw = self.data.get("requests", [])
        self.subjects_data = self.data.get("subjects_js", [])
        self.requests_subjects = self.data.get("requests_subjects", {})

        self.nmts = set(self.data.get("nmts", []))
        self.subid4 = set(i for i in self.data.get("sub4ar", []) if i != 0)

        self.k4max = float(self.data.get("k4max", 0.35))
        self.eb = self.data.get("eb", 40)
        self.rk = self.data.get("rk", 1.0)
        self.okr = self.data.get("okr", 1)
        self._add_subject_coefficients()

    async def decode(self) -> dict:
        """
        Декодує та обробляє всі дані абітурієнтів.

        Returns:
            Оброблений словник з даними
        """
        self.data["requests"] = {}

        for abit_raw in self.requests_raw:
            try:
                # Доповнюємо масив до потрібного розміру
                abit = list(abit_raw) + [0] * (19 - len(abit_raw))

                new_abit = self._create_abiturient(abit)
                new_abit.quota = self._get_quotas(abit)
                new_abit.coef = self._get_coefficients(abit)

                # Обробка балів НМТ
                subjson = self._process_nmt_scores(new_abit, abit)

                # Додаткові коефіцієнти та бали
                self._add_extra_coefficients(subjson, abit)

                # k4max коефіцієнт
                if (
                    self.eb == 40
                    and self.k4max
                    and self._has_subject_for_k4()
                    and len(subjson) > 3
                ):
                    subjson.append({"sb": self.K4MAX, "p": 0, "k": self.k4max})

                # Регіональний коефіцієнт
                if self.rk > 1 and self.eb == 40:
                    subjson.append({"sb": self.RK, "p": 0, "k": self.rk})

                # Генерація посилань
                new_abit.abit_link = generate_link.generate_abit_poisk_link(
                    new_abit.name, self.tg_id
                )
                new_abit.calc_link = generate_link.generate_calc_link(
                    subjson, new_abit.bal, self.eb, self.okr, self.tg_id
                )

                self.data["requests"][new_abit.id] = asdict(new_abit)

                log_parsing_action(
                    self.tg_id,
                    "Processed abiturient",
                    details=f"ID: {new_abit.id}, Name: {new_abit.name}",
                )
            except Exception as e:
                log_error(e, context=f"Error processing abiturient: {abit_raw}")

        self._cleanup_temp_data()
        log_parsing_action(
            self.tg_id,
            "Decoding finished",
            details=f"Processed total: {len(self.data['requests'])}",
        )
        return self.data

    def _create_abiturient(self, abit: list) -> Abiturient:
        """
        Створює об'єкт Abiturient з базовими даними з масиву abit.

        Args:
            abit: Список даних абітурієнта з API

        Returns:
            Abiturient: об'єкт з базовими полями та статусом
        """
        new_abit = Abiturient(
            id=abit[self.ID],
            num=abit[self.NUM],
            priority=max(abit[self.PRIORITY], 0),
            name=abit[self.NAME],
            bal=abit[self.BAL],
            documents="+" if abit[self.DOCUMENTS] == 1 else "-",
            state_education="Б" if abit[self.STATE_EDUCATION] == 1 else "К",
            other_req=(
                abit[self.OTHER_REQ]
                if abit[self.OTHER_REQ]
                and abit[self.OTHER_REQ] != abit[self.PRIORITY]
                and abit[self.REC_TYPE] != -1
                else 0
            ),
        )

        # Визначення статусу
        self._set_status(new_abit, abit)
        return new_abit

    def _set_status(self, new_abit: Abiturient, abit: list) -> None:
        """
        Визначає та встановлює статус абітурієнта залежно від коду статусу,
        типу вступу та реквізитів.

        Args:
            new_abit: об'єкт Abiturient, якому присвоюється статус
            abit: список сирих даних абітурієнта
        """
        status_id = abit[self.STATUS]

        if status_id not in (6, 14):
            new_abit.status = self.statuses.get(str(status_id), "Невідомий статус")
        elif status_id == 14:
            budget_suffix = (
                " (бюджет)" if abit[self.STATE_EDUCATION] == 1 else " (контракт)"
            )
            new_abit.status = (
                self.statuses.get(str(status_id), "Невідомий статус") + budget_suffix
            )
        elif status_id == 6 and abit[self.REC_TYPE]:
            rec_type_key = str(abit[self.REC_TYPE])
            if self.rec_types.get(rec_type_key):
                is_valid_rec_type = (
                    abit[self.OTHER_REQ] == abit[self.PRIORITY]
                    and abit[self.REC_TYPE] != 1
                ) or abit[self.REC_TYPE] == -1
                if is_valid_rec_type:
                    new_abit.rec_type = self.rec_types[rec_type_key]

    def _get_quotas(self, abit: list) -> str:
        """
        Формує рядок з інформацією про квоти абітурієнта.

        Args:
            abit: список сирих даних абітурієнта

        Returns:
            str: рядок з переліком квот
        """
        quotas = []

        if abit[self.QUOTA1]:
            quotas.append("Квота 1")
        if abit[self.QUOTA2]:
            quotas.append("Квота 2")
        if abit[self.QUOTA3]:
            quotas.append("Квота 3")
        if abit[self.INTERVIEW]:
            quotas.append("Вступ за результатами співбесіди")

        return ", ".join(quotas)

    def _get_coefficients(self, abit: list) -> str:
        """
        Обробляє бали НМТ, міжнародні олімпіади та додаткові бали,
        формує subjson і словник nmt_bals для абітурієнта.

        Args:
            new_abit: об'єкт Abiturient, якому будуть додані бали
            abit: список сирих даних абітурієнта

        Returns:
            list: список словників subjson для розрахунку балів
        """
        coefs = []

        if abit[self.COEF_GK] > 1:
            coefs.append("ГК")
        if abit[self.COEF_SK] > 1:
            coefs.append("СК")
        if abit[self.COEF_PCHK] > 0:
            coefs.append("ПЧК")
        if abit[self.COEF_OL] > 0:
            coefs.append("ОЛ")
        if abit[self.COEF_KR] > 0:
            coefs.append("КР")
        if self.rk > 1 and self.eb == 40:
            coefs.append("РК")
        if abit[self.INTERVIEW] > 0:
            coefs.append("СБ")

        return ", ".join(coefs)

    def _process_nmt_scores(self, new_abit: Abiturient, abit: list) -> list:
        """
        Додає додаткові коефіцієнти та бали (ГК, СК, ПЧК, ОЛ) до subjson.

        Args:
            subjson: список суб'єктних записів балів, який буде модифіковано
            abit: список сирих даних абітурієнта
        """
        received_points = self.requests_subjects.get(str(new_abit.id), {})
        subjson = []

        for subject in self.subjects_data:
            sid = str(subject.get("id"))
            if sid not in received_points:
                continue

            scores = received_points[sid]
            ball = scores[0] if scores[0] else 0

            # Міжнародні олімпіади
            if scores[2] == 1:
                ball = 200

            # Додаткові бали
            if scores[1] > 0:
                ball = min(ball + scores[1], 200)

            # Формування subjson
            subject_id = subject["si"]
            if subject_id == self.ATTESTAT and self.eb == 40:
                ballx = (ball - 2) * 10 + 100 if ball >= 2 else 100
                subjson.append({"sb": subject_id, "p": ballx, "k": subject["k"]})
            else:
                entry = {"sb": subject_id, "p": ball, "k": subject["k"]}
                if subject["id"] in self.nmts:
                    entry["nmt"] = 1
                subjson.append(entry)

            # Збереження балів НМТ
            new_abit.nmt_bals[subject.get("s")] = ball

        return subjson

    def _add_extra_coefficients(self, subjson: list, abit: list) -> None:
        """
        Перевіряє наявність предметів, що підпадають під k4 коефіцієнт.

        Returns:
            bool: True, якщо хоча б один предмет підходить, інакше False
        """
        if abit[self.COEF_OL] > 0:
            subjson.append({"sb": self.OL, "p": 10, "k": 1})
        if abit[self.COEF_PCHK] > 0:
            subjson.append({"sb": self.PCHK, "p": 0, "k": abit[self.COEF_PCHK]})
        if abit[self.COEF_SK] > 0:
            subjson.append({"sb": self.SK, "p": 0, "k": abit[self.COEF_SK]})
        if abit[self.COEF_GK] > 1:
            subjson.append({"sb": self.GK, "p": 0, "k": abit[self.COEF_GK]})

    def _has_subject_for_k4(self) -> bool:
        """Перевіряє наявність предмету для k4 коефіцієнта."""
        return any(s["id"] in self.subid4 for s in self.subjects_data)

    def _add_subject_coefficients(self) -> None:
        """
        Створює в data новий ключ "subject_coefficients"
        і вставляє туди данні спочатку про максимальний коефіцієнт для 4 предмета,
        а потім і коефіцієнти всіх інших предметів
        """
        self.data["subject_coefficients"] = {"k4max": self.k4max}
        for subject in self.data.get("subjects_js"):
            self.data["subject_coefficients"][subject["s"]] = subject["k"]

    def _cleanup_temp_data(self) -> None:
        """
        Видаляє тимчасові ключі з словника data після обробки,
        щоб залишилися лише готові дані для зовнішнього використання.
        """
        keys_to_remove = [
            "statuses",
            "rec_types",
            "subjects_js",
            "nmts",
            "eb",
            "sub4ar",
            "k4max",
            "rk",
            "requests_subjects",
        ]
        for key in keys_to_remove:
            self.data.pop(key, None)


# Обгортка для простоти
async def decoder(data: dict, tg_id: int) -> dict:
    """
    Декодує та обробляє дані абітурієнтів.

    Args:
        data: Словник з даними абітурієнтів
        tg_id: Telegram ID користувача

    Returns:
        Оброблений словник з даними
    """
    decoder_instance = AbiturientDecoder(data, tg_id)
    return await decoder_instance.decode()
