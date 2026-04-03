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

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.results_cache import get_result

remove_keyboard = ReplyKeyboardRemove()

admin_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Розпочати аналіз та фільтрацію 📊")],
        [KeyboardButton(text="💸 Донат 💸"), KeyboardButton(text="📑 Про нас 📑")],
        [KeyboardButton(text="📣 Розсилка"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Користувачі"), KeyboardButton(text="📋 Логи")],
        [KeyboardButton(text="👤 Мій профіль")],
    ],
    resize_keyboard=True,
)

user_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Розпочати аналіз та фільтрацію 📊")],
        [KeyboardButton(text="💸 Донат 💸"), KeyboardButton(text="📑 Про нас 📑")],
        [
            KeyboardButton(text="👤 Зв'язок з адміністрацією 👤"),
            KeyboardButton(text="👤 Мій профіль"),
        ],
    ],
    resize_keyboard=True,
)

support = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ До головного меню"),
            KeyboardButton(text="📤 Відправити"),
        ],
    ],
    resize_keyboard=True,
)

return_back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ До головного меню")]], resize_keyboard=True
)

about_us = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💸 Донат 💸"),
            KeyboardButton(text="❌ До головного меню"),
        ],
    ],
    resize_keyboard=True,
)

mailing = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📣 Відправити розсилку"),
            KeyboardButton(text="❌ До головного меню"),
        ],
    ],
    resize_keyboard=True,
)

# --- Profile Keyboards ---


def get_subjects_kb(filled_subjects: dict) -> ReplyKeyboardMarkup:
    """Генерує клавіатуру предметів, позначаючи вже введені."""
    subjects = [
        "Українська мова",
        "Математика",
        "Історія України",
        "Англійська мова",
        "Біологія",
        "Фізика",
        "Хімія",
        "Географія",
        "Українська література",
        "Інша іноземна",
    ]

    buttons = []
    row = []
    for subj in subjects:
        text = subj
        if subj in filled_subjects:
            text = f"✅ {subj}"

        row.append(KeyboardButton(text=text))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append(
        [
            KeyboardButton(text="✅ Завершити введення"),
            KeyboardButton(text="❌ До головного меню"),
        ]
    )

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


settings_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Квоти", callback_data="settings_quotas")],
        [
            InlineKeyboardButton(
                text="🌍 Регіональний коефіцієнт", callback_data="settings_region"
            )
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")],
    ]
)


def get_quotas_kb(active_quotas: list) -> InlineKeyboardMarkup:
    k1_text = "✅ Квота 1" if "kv1" in active_quotas else "Квота 1"
    k2_text = "✅ Квота 2" if "kv2" in active_quotas else "Квота 2"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=k1_text, callback_data="toggle_quota_kv1")],
            [InlineKeyboardButton(text=k2_text, callback_data="toggle_quota_kv2")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")],
        ]
    )


def get_region_kb(is_active: bool) -> InlineKeyboardMarkup:
    text = "✅ Увімкнено" if is_active else "❌ Вимкнено"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data="toggle_region_coef")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")],
        ]
    )


def edit_or_delete_subject_kb(subject: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Змінити бал", callback_data=f"edit_subj_{subject}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Видалити предмет", callback_data=f"del_subj_{subject}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Скасувати", callback_data="cancel_subj_edit"
                )
            ],
        ]
    )


profile_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Редагувати НМТ", callback_data="edit_nmt")],
        [
            InlineKeyboardButton(
                text="⚙️ Налаштування (Квоти/РК)", callback_data="edit_settings"
            )
        ],
        [InlineKeyboardButton(text="📂 Збережені списки", callback_data="saved_lists")],
    ]
)


async def builder_applicant_all(tg_id: int, page: int) -> InlineKeyboardMarkup:
    applicants = InlineKeyboardBuilder()

    result = get_result(tg_id)
    if not result:
        # Якщо кеш пустий, повертаємо порожню клавіатуру з кнопкою назад
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Дані втрачено. Почніть спочатку",
                        callback_data="applicant_back_to_stat",
                    )
                ]
            ]
        )

    competitors_dict = result.get("requests", {}).get("competitors", {})
    non_competitors_dict = result.get("requests", {}).get("non-competitors", {})

    # Об'єднуємо всіх, зберігаючи ID як ключі
    all_list = [(app_id, app) for app_id, app in competitors_dict.items()] + [
        (app_id, app) for app_id, app in non_competitors_dict.items()
    ]
    # Сортуємо за балом (спадання)
    all_list.sort(key=lambda x: x[1].get("score", 0), reverse=True)

    per_page = 10
    total_pages = (len(all_list) + per_page - 1) // per_page
    if total_pages == 0:
        total_pages = 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    current_page_applicants = all_list[start:end]

    for applicant_id, app in current_page_applicants:
        applicant_name = " ".join(app.get("name", "").split(" ")[:2])
        score = app.get("score", 0)
        # Маркуємо, якщо це конкурент (перевіримо обидва формати ключа)
        marker = (
            "🔴"
            if (
                applicant_id in competitors_dict
                or str(applicant_id) in competitors_dict
            )
            else "🟢"
        )

        applicants.button(
            text=f"{marker} {applicant_name} | {score}",
            callback_data=f"applicant_{applicant_id}",
        )
    applicants.adjust(1)

    nav_buttons = InlineKeyboardBuilder()
    if page > 1:
        nav_buttons.button(text="◀️", callback_data=f"applicant_page_{page - 1}")
    nav_buttons.button(
        text=f"{page}/{total_pages}",
        callback_data="applicant_back_to_stat",
    )
    if page < total_pages:
        nav_buttons.button(text="▶️", callback_data=f"applicant_page_{page + 1}")
    nav_buttons.adjust(3)

    applicants.attach(nav_buttons)

    return applicants.as_markup()


async def builder_applicant_competitors(
    tg_id: int, user_score: float, page: int
) -> InlineKeyboardMarkup:
    applicants = InlineKeyboardBuilder()

    result = get_result(tg_id)
    if not result:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Дані втрачено", callback_data="applicant_back_to_stat"
                    )
                ]
            ]
        )

    competitors = result.get("requests", {}).get("competitors", {})

    comp_list = [(app_id, app) for app_id, app in competitors.items()]
    # Сортуємо за балом
    comp_list.sort(key=lambda x: x[1].get("score", 0), reverse=True)

    per_page = 10
    total_pages = (len(comp_list) + per_page - 1) // per_page
    if total_pages == 0:
        total_pages = 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    current_page_competitors = comp_list[start:end]

    for applicant_id, app in current_page_competitors:
        applicant_name = " ".join(app.get("name", "").split(" ")[:2])
        applicants.button(
            text=f"🔴 {applicant_name} | {app.get('score', 0)}",
            callback_data=f"applicant_{applicant_id}",
        )
        applicants.adjust(1)

    nav_buttons = InlineKeyboardBuilder()
    if page > 1:
        nav_buttons.button(text="◀️", callback_data=f"competitors_page_{page - 1}")
    nav_buttons.button(
        text=f"{page}/{total_pages}",
        callback_data="applicant_back_to_stat",
    )
    if page < total_pages:
        nav_buttons.button(text="▶️", callback_data=f"competitors_page_{page + 1}")
    nav_buttons.adjust(3)

    applicants.attach(nav_buttons)

    return applicants.as_markup()


def builder_applicant_details(
    applicant_id: int, is_threat: bool
) -> InlineKeyboardMarkup:
    """Клавіатура для деталей абітурієнта з можливістю тогла."""
    kb = InlineKeyboardBuilder()

    # Кнопка перемикання
    if is_threat:
        kb.button(
            text="❌ Це не конкурент", callback_data=f"toggle_threat_{applicant_id}"
        )
    else:
        kb.button(
            text="✅ Вважати конкурентом", callback_data=f"toggle_threat_{applicant_id}"
        )

    kb.button(text="📋 Інші заяви", callback_data=f"show_abit_history_{applicant_id}")
    kb.button(
        text="⬅️ Назад до списку", callback_data="applicant_back_to_list"
    )  # Повертає туди, звідки прийшли (All або Competitors)
    kb.adjust(1)
    return kb.as_markup()


applicant_stat = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Всі абітурієнти", callback_data="view_applicant_all"
            ),
            InlineKeyboardButton(
                text="🎯 Тільки конкуренти", callback_data="view_applicant_competitors"
            ),
        ],
        [InlineKeyboardButton(text="💾 Зберегти список", callback_data="save_list")],
    ]
)
