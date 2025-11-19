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

# user_info = {
#     "Українська мова": 145.3,
#     "Математика": 154.3,
#     "Історія України": 144.0,
#     "Українська література": 0,
#     "Іноземна мова": 0,
#     "Біологія": 0,
#     "Географія": 0,
#     "Фізика": 154.3,
#     "Хімія": 0,
#     "Творчий конкурс": 154.0,
# }

# "subject_coefficients": {
#     "k4max": 0.1,
#     "Українська мова": 0.1,
#     "Математика": 0.1,
#     "Історія України": 0.1,
#     "Українська література": 0.1,
#     "Іноземна мова": 0.1,
#     "Біологія": 0.1,
#     "Географія": 0.1,
#     "Фізика": 0.1,
#     "Хімія": 0.1,
#     "Творчий конкурс": 0.6,
# }


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
        return 0.0

    rating_score = (
        numerator / denominator
    )  # ! Дописати сюди ще ОУ, але я хз як воно відображається в API

    return rating_score if rating_score < 200.0 else 200.0


def filter_data(data: dict, tg_id: int) -> dict:
    """Функція приймає телеграм id, дані які треба профільтрувати і фільтрує їх за алгоритмом. Повертає результат фільтрації"""
    filtred_data = data.copy()

    # TODO: Дописати фільтр


# Написати попередження, типу якщо є творчий конкурс, то я не зможу правильно і точно обробити шанси, але на свій страх і ризик можна ввести приблизний бал, який ти можеш отримати за творчий конкурс
