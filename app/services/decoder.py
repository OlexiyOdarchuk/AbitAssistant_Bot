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
    documents: bool = False
    rec_type: str = ""
    state_education: bool = False
    other_req: int = 0
    nmt_bals: dict = field(default_factory=dict)


async def decoder(data: dict, tg_id: int) -> dict:
    new_data = data.copy()
    statuses = new_data.get("statuses", {})
    rec_types = new_data.get("rec_types", {})
    requests = new_data.get("requests", [])
    new_data["requests"] = {}
    for abit in requests:
        # Якщо абітурієнт коротший, ніж требп, заповнюємо 0
        abit = list(abit) + [0] * (19 - len(abit))

        new_abit = Abiturient(
            id=abit[0],
            num=abit[1],
            state_education=True if abit[17] == 1 else False,
            priority=abit[2] if abit[2] > 0 else 0,
            name=abit[4],
            bal=abit[5],
            documents=True if abit[14] == 1 else False,
            other_req=(
                abit[18] if abit[18] and abit[18] != abit[2] and abit[15] != -1 else 0
            ),
        )

        # статус
        if abit[3] not in (6, 14):
            new_abit.status = statuses.get(str(abit[3]), "Невідомий статус")
        elif abit[3] == 14:
            new_abit.status = statuses.get(str(abit[3]), "Невідомий статус") + (
                " (бюджет)" if abit[17] == 1 else " (контракт)"
            )
        elif (
            abit[3] == 6
            and abit[15]
            and rec_types.get(str(abit[15]))
            and ((abit[18] == abit[2] and abit[15] != 1) or abit[15] == -1)
        ):
            new_abit.rec_type = rec_types.get(str(abit[15]))

        # квоти
        quotas = []
        if abit[6]:
            quotas.append("Квота 1")
        if abit[7]:
            quotas.append("Квота 2")
        if abit[8]:
            quotas.append("Квота 3")
        if abit[16]:
            quotas.append("Вступ за результатами співбесіди")
        new_abit.quota = ", ".join(quotas) if quotas else ""

        # коефіцієнти
        coefs = []
        if abit[9] > 1:
            coefs.append("ГК")
        if abit[10] > 1:
            coefs.append("СК")
        if abit[11] > 0:
            coefs.append("ПЧК")
        if abit[12] > 0:
            coefs.append("ОЛ")
        if abit[13] > 0:
            coefs.append("КР")
        new_abit.coef = ", ".join(coefs) if coefs else ""

        # Бали НМТ
        received_points = new_data.get("requests_subjects", {}).get(
            str(new_abit.id), {}
        )
        subjects_data = new_data.get("subjects_js")

        for i in subjects_data:
            if str(i.get("id")) in received_points:
                new_abit.nmt_bals[i.get("s")] = received_points.get(str(i.get("id")))

        new_data["requests"][new_abit.id] = new_abit

    requests = {k: asdict(v) for k, v in new_data.get("requests").items()}
    new_data["requests"] = requests
    new_data.pop("requests_subjects")

    return new_data
