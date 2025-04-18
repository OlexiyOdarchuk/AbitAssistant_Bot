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

async def all_applicant_len(tg_id:int) -> int:
    data = await rq.get_user_data(tg_id)
    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id]
    return len(user_applicants)

async def competitors_applicant_len(tg_id:int) -> int:
    data = await rq.get_user_data(tg_id)
    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id and applicant.competitor]
    return len(user_applicants)
