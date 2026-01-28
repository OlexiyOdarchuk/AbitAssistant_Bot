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

import asyncio
import re
from app.database.requests import (
    get_user_nmt,
    get_user_settings,
    get_cached_competitor,
    cache_competitor,
)
from app.services.parse_abit_poisk import fetch_applicant_data
from app.services.logger import log_parsing_action, log_error, log_system_event

REQUIRED_SUBJECTS = {"Українська мова", "Математика", "Історія України"}


async def calculate_rating_score(
    subject_coefficients: dict, tg_id: int, creative_contest_score: float = 0
) -> float:
    """Функція, що обраховує рейтинговий бал на спеціальність виходячи з балів нмт користувача"""
    user_scores = await get_user_nmt(tg_id)
    user_settings = await get_user_settings(tg_id)

    if not user_scores:
        log_error(f"User {tg_id} has no NMT scores", "Calculation aborted")
        return 0.0

    # Пошук 4-го предмета (вибіркового) - НЕ включаючи творчий конкурс
    additional_subject = None
    
    best_additional_score = 0
    
    for subject, score in user_scores.items():
        # Пропускаємо творчий конкурс в пошуку 4-го предмета
        if subject not in REQUIRED_SUBJECTS and subject.lower() != "творчий конкурс":
            coef = subject_coefficients.get(subject, 0)
            if coef > 0:
                current_val = score * coef
                if additional_subject is None or current_val > best_additional_score:
                    additional_subject = subject
                    best_additional_score = current_val

    sum_scores = 0
    sum_coeffs = 0

    for subject in REQUIRED_SUBJECTS:
        score = user_scores.get(subject, 0)
        coef = subject_coefficients.get(subject, 0)
        sum_scores += score * coef
        sum_coeffs += coef

    # Додатковий предмет (але НЕ творчий конкурс)
    if additional_subject:
        score = user_scores.get(additional_subject, 0)
        coef = subject_coefficients.get(additional_subject, 0)
        sum_scores += score * coef
        sum_coeffs += coef
    
    # Творчий конкурс - ТІЛЬКИ якщо користувач явно вказав його бал
    if creative_contest_score > 0:
        coef_cc = subject_coefficients.get("Творчий конкурс", 0)
        if coef_cc > 0:
            sum_scores += creative_contest_score * coef_cc
            sum_coeffs += coef_cc

    if sum_coeffs == 0:
        return 0.0

    rating_score = sum_scores / sum_coeffs
    
    # Регіональний коефіцієнт
    if user_settings.get("region_coef"):
        rk_val = subject_coefficients.get("rk", 1.0)
        if rk_val > 1:
             rating_score *= rk_val
        else:
             # Якщо парсер не знайшов РК, але юзер каже "Так", зазвичай це не застосовується автоматично
             pass
    
    return round(rating_score, 3) if rating_score <= 200.0 else 200.0


async def check_competitor_threat(name: str, current_priority: int, tg_id: int = 0) -> bool:
    try:
        cached_data = await get_cached_competitor(name)
        
        if cached_data is None:
            cached_data = await fetch_applicant_data(name, tg_id)
            await cache_competitor(name, cached_data)
            await asyncio.sleep(0.5)

        if not cached_data:
            return True

        for app in cached_data:
            try:
                app_priority = int(app.get("priority", 99))
            except ValueError:
                continue 

            if app_priority < current_priority:
                status = app.get("status", "").lower()
                
                # Якщо статус містить "деактивовано" - людина вже зарахована на іншу програму, не загроза
                if "деактивовано" in status:
                    return False
                
                # Якщо статус "рекомендовано" або "до наказу" - людина займає місце на іншій програмі з вищим пріоритетом
                # Вона мало ймовірно прийме цю програму, але технічно все ще конкурент (може відмовитися)
                # Залишаємо як потенційну загрозу

        return True 
    except Exception as e:
        log_error(e, f"Error checking competitor {name}")
        return True


def parse_volume_limit(volume_data: dict, key_substring: str) -> int:
    for key, value in volume_data.items():
        if key_substring in key:
            try:
                return int(value)
            except ValueError:
                return 0
    return 0


async def recalculate_analysis(data: dict, tg_id: int) -> dict:
    """
    Перераховує статистику (шанси, ранги) на основі поточних списків competitors/non-competitors.
    Не робить мережевих запитів.
    """
    user_settings = await get_user_settings(tg_id)
    user_quotas = user_settings.get("quotas", [])
    user_score = data.get("user_rating_score", 0)
    
    volume_data = data.get("volume", {})
    
    # Спроба знайти загальний обсяг за різними ключами
    total_budget_volume = parse_volume_limit(volume_data, "Максимальний обсяг державного замовлення")
    if total_budget_volume == 0:
        total_budget_volume = parse_volume_limit(volume_data, "Обсяг держзамовлення")
    if total_budget_volume == 0:
        total_budget_volume = parse_volume_limit(volume_data, "Загальний обсяг бюджетних місць")
        
    quota1_volume = parse_volume_limit(volume_data, "Квота 1")
    quota2_volume = parse_volume_limit(volume_data, "Квота 2")
    
    # Якщо не вдалося знайти обсяги, то аналіз неможливо виконати
    if total_budget_volume <= 0:
        log_parsing_action(tg_id, f"WARNING: Could not determine budget volume. Analysis may be inaccurate.")
        # Встановимо мінімальні значення для продовження
        total_budget_volume = max(1, len(list(competitors)) + 1)
    
    competitors = data.get("requests", {}).get("competitors", {}).values()
    
    # Розподіляємо конкурентів (тільки тих, хто зараз в списку competitors)
    q1_list = []
    q2_list = []
    general_list = []
    
    # Окремо рахуємо людей, які вже зарахвані ("до наказу" або "рекомендовано")
    already_enrolled_count = 0
    
    for req in competitors:
        status = req.get("status", "").lower()
        
        # Люди з "до наказу" або "рекомендовано" вже займають місця
        if "до наказу" in status or "рекомендовано" in status:
            already_enrolled_count += 1
            continue
        
        quotas_str = req.get("quota", "")
        if "КВ1" in quotas_str:
            q1_list.append(req)
        elif "КВ2" in quotas_str:
            q2_list.append(req)
        else:
            general_list.append(req)
            
    # Заповнюємо квоти
    q1_taken = min(len(q1_list), quota1_volume)
    q2_taken = min(len(q2_list), quota2_volume)
    
    # Обраховуємо скільки осіб з загального конкурсу займають місця
    general_taken = min(len(general_list), max(0, total_budget_volume - q1_taken - q2_taken))
    
    # Вільні місця = всього місць - люди по квотах - люди з загального - люди які вже зарахвані
    remaining_spots = total_budget_volume - q1_taken - q2_taken - general_taken - already_enrolled_count
    
    chance = "Unknown"
    advice = ""
    my_real_rank = 0
    
    if "КВ1" in user_quotas:
        my_q_rank = sum(1 for r in q1_list if r["score"] > user_score) + 1
        my_real_rank = my_q_rank
        if my_q_rank <= quota1_volume:
            chance = "High (Quota 1)"
            advice = f"Ви проходите по Квоті 1! ({my_q_rank}-й з {quota1_volume} місць)"
            
    elif "КВ2" in user_quotas:
         my_q_rank = sum(1 for r in q2_list if r["score"] > user_score) + 1
         my_real_rank = my_q_rank
         if my_q_rank <= quota2_volume:
            chance = "High (Quota 2)"
            advice = f"Ви проходите по Квоті 2! ({my_q_rank}-й з {quota2_volume} місць)"
    
    if chance == "Unknown":
        # Загальний конкурс - рахуємо людей без квот
        competitors_ahead = sum(1 for r in general_list if r["score"] > user_score)
        my_real_rank = competitors_ahead + 1
        
        if remaining_spots <= 0:
            chance = "Zero"
            advice = "Бюджетних місць для загального конкурсу не залишилось."
        elif my_real_rank <= remaining_spots:
            chance = "High"
            advice = f"Ви {my_real_rank}-й претендент на {remaining_spots} вільних місць. Шанси чудові! 🎉"
        elif my_real_rank <= remaining_spots + 5:
            chance = "Medium"
            advice = f"Ви {my_real_rank}-й на {remaining_spots} місць. Є шанс, що {my_real_rank - remaining_spots} людей відмовляться."
        else:
            chance = "Low"
            advice = f"Ви {my_real_rank}-й, а місць лише {remaining_spots}. Шанси малі. 😔"

    data["analysis"] = {
        "chance": chance,
        "advice": advice,
        "total_budget": total_budget_volume,
        "remaining_general": remaining_spots,
        "my_real_rank": my_real_rank
    }
    return data


async def filter_data(data: dict, tg_id: int, creative_contest_score: float = 0) -> dict:
    subject_coefficients = data.get("subject_coefficients", {})
    user_score = await calculate_rating_score(subject_coefficients, tg_id, creative_contest_score)
    user_settings = await get_user_settings(tg_id)
    user_quotas = user_settings.get("quotas", [])

    log_parsing_action(tg_id, f"User score: {user_score}, Quotas: {user_quotas}")

    requests = data.get("requests", {})
    
    competitors = {}
    non_competitors = {}
    
    tasks = []
    task_map = {}

    sorted_requests = sorted(requests.values(), key=lambda x: x["score"], reverse=True)

    for req in sorted_requests:
        abit_id = req["id"]
        priority = req["priority"]
        name = req["name"]
        
        if not req.get("state_education", True) or priority <= 0:
            req["filter_reason"] = "Contract"
            non_competitors[abit_id] = req
            continue

        # Check if already enrolled elsewhere (деактивовано = enrolled at another program)
        # These people are NOT competitors because they took a spot elsewhere, not here
        status = req.get("status", "").lower()
        if "деактивовано" in status:
            req["filter_reason"] = "Already enrolled elsewhere"
            non_competitors[abit_id] = req
            continue

        # People with "до наказу" or "рекомендовано" ARE competitors because they occupy spots on THIS program
        # Also check for variations with spaces and brackets
        if ("до наказу" in status or "рекомендовано" in status or 
            "до наказу" in status.replace(" ", "") or "доналказу" in status.replace(" ", "")):
            req["filter_reason"] = "Recommended/To order (occupies spot)"
            competitors[abit_id] = req
            continue

        if req["score"] < user_score:
             req["filter_reason"] = "Lower Score"
             non_competitors[abit_id] = req
             continue
        
        if priority == 1:
            # Люди з пріоритетом 1 - конкуренти
            competitors[abit_id] = req
            continue
            
        task = asyncio.create_task(check_competitor_threat(name, priority, tg_id))
        tasks.append(task)
        task_map[task] = (abit_id, req)

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for task, result in zip(tasks, results):
            abit_id, req = task_map[task]
            
            is_real_threat = True
            if not isinstance(result, Exception) and result is False:
                is_real_threat = False
            
            if is_real_threat:
                competitors[abit_id] = req
            else:
                req["filter_reason"] = "Passed elsewhere"
                non_competitors[abit_id] = req

    # Оновлення словника з даними
    final_competitors = {}
    for aid, req in competitors.items():
        # People with "до наказу" or "рекомендовано" ALWAYS stay as competitors (they occupy spots)
        status = req.get("status", "").lower()
        if "до наказу" in status or "рекомендовано" in status:
            final_competitors[aid] = req
            continue
        
        is_q = "КВ" in req.get("quota", "")
        if is_q and "КВ" not in user_quotas:
             final_competitors[aid] = req
             continue
             
        if req["score"] > user_score:
            final_competitors[aid] = req
        else:
            req["filter_reason"] = "Lower Score"
            non_competitors[aid] = req

    new_data = data.copy()
    new_data["requests"] = {
        "competitors": final_competitors,
        "non-competitors": non_competitors
    }
    new_data["user_rating_score"] = user_score
    
    new_data = await recalculate_analysis(new_data, tg_id)
    
    return new_data