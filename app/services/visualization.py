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

import matplotlib.pyplot as plt
import io
from aiogram.types import BufferedInputFile


def generate_rating_histogram(
    data: dict, user_score: float, title: str = "Розподіл балів"
) -> BufferedInputFile:
    """
    Генерує гістограму розподілу балів абітурієнтів.

    Args:
        data: Повний словник даних (результат аналізу).
        user_score: Бал поточного користувача.
        title: Заголовок графіку.

    Returns:
        BufferedInputFile: Зображення для відправки в Telegram.
    """

    # Збираємо всі бали
    competitors = data.get("requests", {}).get("competitors", {}).values()
    non_competitors = data.get("requests", {}).get("non-competitors", {}).values()

    scores = []

    # Додаємо бали реальних конкурентів
    for req in competitors:
        try:
            scores.append(float(req.get("score", 0)))
        except (ValueError, TypeError):
            continue

    # Додаємо бали не конкурентів (для загальної картини)
    for req in non_competitors:
        try:
            # Тільки якщо це не контракт (бо контрактники часто мають низькі бали і псують графік)
            # Або якщо в них є бал > 100
            s = float(req.get("score", 0))
            if s > 100:
                scores.append(s)
        except (ValueError, TypeError):
            continue

    if not scores:
        return None

    # Налаштування стилю
    plt.style.use("dark_background")  # Темна тема під Telegram
    fig, ax = plt.subplots(figsize=(10, 6))

    # Будуємо гістограму
    bins = range(100, 201, 5)  # Крок 5 балів
    n, bins, patches = ax.hist(
        scores, bins=bins, color="#3498db", alpha=0.7, edgecolor="white"
    )

    # Підсвічуємо бали вище користувача (червоним)
    for i in range(len(patches)):
        if bins[i] >= user_score:
            patches[i].set_facecolor("#e74c3c")  # Red for danger
        else:
            patches[i].set_facecolor("#2ecc71")  # Green for safe

    # Лінія користувача
    ax.axvline(
        user_score,
        color="yellow",
        linestyle="dashed",
        linewidth=2,
        label=f"Ваш бал: {user_score:.2f}",
    )

    # Оформлення
    ax.set_title(title, fontsize=16, fontweight="bold", color="white", pad=20)
    ax.set_xlabel("Конкурсний бал", fontsize=12, color="white")
    ax.set_ylabel("Кількість заяв", fontsize=12, color="white")
    ax.legend(loc="upper left", frameon=True, facecolor="#333333", edgecolor="white")
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Додаємо текст про конкурентів
    count_higher = sum(1 for s in scores if s > user_score)
    count_total = len(scores)

    stats_text = (
        f"Всього заяв: {count_total}\n"
        f"Вище вас: {count_higher}\n"
        f"Нижче вас: {count_total - count_higher}"
    )

    # Текстовий бокс
    props = dict(boxstyle="round", facecolor="#333333", alpha=0.8, edgecolor="white")
    ax.text(
        0.98,
        0.95,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=props,
        color="white",
    )

    # Збереження в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return BufferedInputFile(buf.read(), filename="stats_graph.png")
