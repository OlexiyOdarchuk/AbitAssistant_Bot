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

from app.database.requests import get_user_info
from logger import log_parsing_action, log_error
import pandas as pd


def calculate_rating_score(
    subject_coefficients: dict, tg_id: int, creative_contest_score: float = 0
) -> float:
    """Функція, що обраховує рейтинговий бал на спеціальність виходячи з балів нмт користувача

    Args:
        subject_coefficients (dict): Коефіцієнти на предмети
        tg_id (int): телеграм ID
        creative_contest (float): бал за творчий конкурс

    Returns:
        float: рейтинговий бал
    """
    user_scores = get_user_info(tg_id)  # Витягуються дані користувача

    REQUIRED_SUBJECTS = {"Українська мова", "Математика", "Історія України"}

    additional_subject = None
    for subject in user_scores.keys():  # Дістаємо 4 предмет
        if subject not in REQUIRED_SUBJECTS and user_scores.get(subject):
            additional_subject = subject
            log_parsing_action(tg_id, "Дістав 4 предмет", subject)
            break

    numerator = (
        # Обрахунок чисельника
        sum(
            user_scores.get(subject, 0) * subject_coefficients.get(subject, 0)
            for subject in REQUIRED_SUBJECTS
        )
        + user_scores.get(additional_subject, 0)
        * subject_coefficients.get(additional_subject, 0)
        + creative_contest_score * subject_coefficients.get("Творчий конкурс", 0)
        # Якщо балу за творчий конкурс немає, там просто +0 вийде
    )

    denominator = (  # Обрахунок знаменника
        sum(subject_coefficients.get(subject, 0) for subject in REQUIRED_SUBJECTS)
        + (
            (
                subject_coefficients.get("k4max", 0)
                + subject_coefficients.get(additional_subject, 0)
            )
            / 2
            + subject_coefficients.get("Творчий конкурс", 0)
        )
    )

    if denominator == 0:
        log_error(f"Під час обчислення рейтингового балу {tg_id} знаменник 0")
        return 0.0

    rating_score = numerator / denominator
    log_parsing_action(tg_id, "Облислено рейтонговий бал", rating_score)
    return round(rating_score, 3) if rating_score < 200.0 else 200.0


def filter_data(data: dict, tg_id: int, creative_contest_score: float = 0) -> dict:
    """Функція приймає дані які треба профільтрувати, телеграм id, і фільтрує їх за алгоритмом.
    Повертає такий же словник з данними, але в requests тепер всередині 2 словника: competitors і non-competitors"""

    user_rating_score = calculate_rating_score(
        data.get("subject_coefficients", {}), tg_id, creative_contest_score
    )
    filtred_requests = {"competitors": {}, "non-competitors": {}}
    df = pd.DataFrame.from_dict(data.get("requests", {}), orient="index")

    if df.empty:  # Перевірка на пустий словник
        log_error(
            "Пустий словник",
            f"Під час фільтрації виявилося, що у {tg_id} немає абітурієнтів на парс",
        )
        data["requests"] = filtred_requests
        return data

    df = df.rename_axis("abit_id").reset_index()

    # Ті, хто на бюджеті
    df = df[df["state_education"]]

    # Квота
    quota1_limit = int(data["volume"].get("Максимальне держзамовлення, квота 1", 0))

    if quota1_limit > 0:
        real_quota1 = (
            df[df["quota"] == "КВ1"]
            .sort_values("score", ascending=False)  # Сортування за балом
            .reset_index(drop=True)
            .iloc[:quota1_limit]  # Обмеження максимальної кількості
            .sort_values("num", ascending=True)  # Повернення на норм порядок
        )
    else:
        real_quota1 = pd.DataFrame()

    quota2_limit = int(data["volume"].get("Максимальне держзамовлення, квота 2", 0))

    if quota2_limit > 0:
        real_quota2 = (
            df[df["quota"] == "КВ2"]
            .sort_values("score", ascending=False)  # Сортування за балом
            .reset_index(drop=True)
            .iloc[:quota2_limit]  # Обмеження максимальної кількості
            .sort_values("num", ascending=True)  # Повернення на норм порядок
        )
    else:
        real_quota2 = pd.DataFrame()

    # Ті, в кого просто більше балів
    high_score_competitors = df[df["score"] > user_rating_score]

    # Наповнення competitors
    filtred_requests["competitors"] = (
        pd.concat([real_quota1, real_quota2, high_score_competitors])
        .drop_duplicates(subset=["abit_id"])
        .sort_values(by="num", ascending=True)
        .set_index("abit_id")
        .to_dict(orient="index")
    )

    # Наповнення non-competitors
    all_abit_ids = set(data.get("requests", {}).keys())
    competitor_ids = set(filtred_requests["competitors"].keys())
    non_competitor_ids = all_abit_ids - competitor_ids

    filtred_requests["non-competitors"] = {
        abit_id: data["requests"][abit_id] for abit_id in non_competitor_ids
    }

    new_data = data.copy()
    new_data["requests"] = filtred_requests
    new_data["user_rating_score"] = user_rating_score
    log_parsing_action(tg_id, "Профільтравано абітурієнтів")
    return new_data


# Написати попередження, типу якщо є творчий конкурс, то я не зможу правильно і точно обробити шанси, але на свій страх і ризик можна ввести приблизний бал, який ти можеш отримати за творчий конкурс
