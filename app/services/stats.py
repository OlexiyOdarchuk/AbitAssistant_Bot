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

import app.database.requests as rq

user_score = {}

async def all_applicant_len(tg_id:int) -> int:
    """Рахує загальну кількість заявок."""
    data = await rq.get_user_data(tg_id)
    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id]
    return len(user_applicants)

async def competitors_applicant_len(tg_id:int) -> int:
    """Рахує кількість заявок конкурентів."""
    data = await rq.get_user_data(tg_id)
    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id and applicant.competitor]
    return len(user_applicants)

async def admin_statistics() -> str:
    user_count = await rq.get_user_count()
    total_stats = await rq.get_total_activates()
    total_right_activates = total_stats["total_right_activates"]
    total_activates = total_stats["total_activates"]
    top_user = await rq.get_top_user()
    top_user_id = top_user["tg_id"] if top_user else "ВІДСУТНІЙ"
    top_user_activates = top_user["activates"] if top_user else 0
    failed_activates = total_activates - total_right_activates

    return f"""
📊 Статистика AbitAssistant_bot:

👥 Кількість користувачів: {user_count}
⚙️ Всього активацій: {total_activates}
❌ З них завершилися з помилкою: {failed_activates}
🏆 Найактивніший користувач: tg://user?id={top_user_id} — {top_user_activates} активацій"""
