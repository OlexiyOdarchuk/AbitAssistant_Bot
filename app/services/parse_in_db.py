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

from app.services.generate_link import generate_link
from app.database.requests import clear_user_data, set_user_data
from config import user_score


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


def is_competitor(score: float, priority: int, quota: str, tg_id: int) -> bool:
    """
    Визначає, чи є абітурієнт конкурентом:
    - Якщо є квота - перевіряє тільки пріоритет.
    - Якщо квоти немає - перевіряє бали проти балу користувача, а потім пріоритет.
    """
    base_score = user_score.get(tg_id, 0.0)
    has_quota = bool(quota and quota.strip())

    if has_quota:
        return priority <= 3
    # без квоти
    if score > base_score:
        return priority <= 3
    return False


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
        raise ValueError('Таблиця не знайдена на сторінці.')

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
            priority = 99

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
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--loglevel=3")

    driver = await fetch_driver(url, chrome_options)
    try:
        await clear_user_data(tg_id)
        await click_all_details(driver)
        rows = await parse_rows(driver)

        excluded_statuses = ('Відхилено', 'Відмовлено', 'Скасовано')

        new_user_data = []

        for idx, row in enumerate(rows, start=1):
            if row['app_type'].upper() == 'К':
                continue

            if any(bad_word in row['status'].lower() for bad_word in excluded_statuses):
                continue

            competitor = is_competitor(
                row['score'], row['priority'], row['quota'], tg_id
            )
            link = await generate_link(row['name'])

            new_user_data.append({
                'name': row['name'],
                'status': row['status'],
                'priority': row['priority'],
                'score': row['score'],
                'detail': row['detail'],
                'coefficient': row['coefficient'],
                'quota': row['quota'],
                'link': link,
                'competitor': competitor
            })

        await set_user_data(tg_id=tg_id, new_user_data=new_user_data)

    except Exception as e:
        print(f"❌ Сталася помилка: {e}")
    finally:
        await asyncio.to_thread(driver.quit)
