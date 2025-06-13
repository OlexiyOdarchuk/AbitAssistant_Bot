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
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import tempfile

from app.services.generate_link import generate_link
import app.database.requests as rq
import app.services.stats as stats
from config import ADMIN_ID

def clean_score(raw_score: str) -> float:
    """
    Очищує сирий рядок балу, витягує перше числове значення та конвертує у float.
    Повертає 0.0, якщо не вдається знайти число.
    """
    try:
        match = re.search(r"\d+[\d\.,]*", raw_score.replace('–', '').replace('-', ''))
        if match:
            num_str = match.group(0).replace(',', '.')
            return float(num_str)
        return 0.0
    except Exception:
        return 0.0


def has_quota_or_coefficient(quota: str, coefficient: str) -> bool:
    """Перевірка на наявність квоти або коефіцієнту"""
    quota_codes = {'КВ1', 'КВ2', 'ПО', 'СБ'}
    coefficient_codes = {'РК', 'ГК', 'ОУ'}

    quota_set = set(q.strip().upper() for q in (quota or '').split(',') if q.strip())
    coefficient_set = set(c.strip().upper() for c in (coefficient or '').split(',') if c.strip())

    return bool(quota_codes.intersection(quota_set)) or bool(coefficient_codes.intersection(coefficient_set))


def is_valid_status(status: str) -> bool:
    """Статуси, які виключаються (враховуючи всі варіанти)"""

    excluded_statuses = [
        'відмова', 'скасовано', 'затримано', 'відхилено', 'відмовлено', 'скасовано (втрата пріор.)'
    ]
    status_lower = status.lower()
    return not any(excluded in status_lower for excluded in excluded_statuses)


def is_competitor(score: float, priority: int, quota: str, coefficient: str, tg_id: int) -> bool:
    base_score = stats.user_score.get(tg_id, 0.0)
    has_quota_coeff = has_quota_or_coefficient(quota, coefficient)

    if has_quota_coeff:
        return priority <= 3
    else:
        return score > base_score and priority <= 3


async def fetch_driver(url: str, chrome_options: Options):
    driver = await asyncio.to_thread(webdriver.Chrome, options=chrome_options)
    await asyncio.to_thread(driver.get, url)
    await asyncio.to_thread(time.sleep, 2)
    return driver


async def click_all_details(driver):
    """Клікає на кнопку 'Завантажити ще'."""
    while True:
        elements = await asyncio.to_thread(driver.find_elements, By.CLASS_NAME, "detail-link")
        if not elements:
            break
        clicked = False
        for el in elements:
            if el.is_displayed():
                await asyncio.to_thread(driver.execute_script, "arguments[0].click();", el)
                await asyncio.to_thread(time.sleep, 1)
                clicked = True
        if not clicked:
            break


async def parse_rows(driver) -> list[dict]:
    """Парсить дані з таблиці на сторінці."""
    html = await asyncio.to_thread(lambda: driver.page_source)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='rwd-table')
    if not table:
        return []

    rows = table.find_all('tr')[1:]
    results = []

    for idx, row in enumerate(rows, start=1):
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(cells) < 9:
            print(f"⚠️ Рядок {idx}: недостатньо даних ({len(cells)} клітинок)")
            continue

        raw_score = cells[4]
        score = clean_score(raw_score)
        try:
            priority = int(cells[3])
        except ValueError:
            priority = 0

        results.append({
            'name': cells[1],
            'status': cells[2],
            'priority': priority,
            'raw_score': raw_score,
            'score': score,
            'detail': cells[5],
            'coefficient': cells[6],
            'quota': cells[7],
            'app_type': cells[8],
        })

    return results


async def parser(url: str, tg_id: int):
    """Працює з сторінкою, обробляє дані і зберігає їх у базі даних."""
    if tg_id not in ADMIN_ID:
        await rq.update_user_activates(tg_id)

    user_data_dir = tempfile.mkdtemp(prefix=f"chromium_{tg_id}")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--log-level=3")

    driver = await fetch_driver(url, chrome_options)
    try:
        await rq.clear_user_data(tg_id)
        await click_all_details(driver)
        rows = await parse_rows(driver)

        new_user_data = []

        if rows:

            for row in rows:
                # Відкидаємо контрактні заявки (тип 'К')
                if row['app_type'].upper() == 'К':
                    continue

            # Фільтрація по статусу
                if not is_valid_status(row['status']):
                    continue

                competitor = is_competitor(
                    row['score'], row['priority'], row['quota'], row['coefficient'], tg_id
                )
                link = await generate_link(row['name'])

                coeff = row['coefficient'] if row['coefficient'] else '-'
                quota = row['quota'] if row['quota'] else '-'

                new_user_data.append({
                    'name': row['name'],
                    'status': row['status'],
                    'priority': row['priority'],
                    'score': row['score'],
                    'detail': row['detail'],
                    'coefficient': coeff,
                    'quota': quota,
                    'link': link,
                    'competitor': competitor
                })
            if tg_id not in ADMIN_ID:
                await rq.update_user_right_activates(tg_id)
            await rq.set_user_data(tg_id=tg_id, new_user_data=new_user_data)

        else:
            return "Error"

    except Exception as e:
        print(f"❌ Сталася помилка: {e}")
    finally:
        await asyncio.to_thread(driver.quit)
