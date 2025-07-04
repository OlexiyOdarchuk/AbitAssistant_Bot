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
from app.services.logger import log_parsing_action, log_parsing_step, log_error, log_user_action
import app.database.requests as rq
import app.services.stats as stats
from config import ADMIN_ID

def clean_score(raw_score: str) -> float:
    """
    Очищує сирий рядок балу, витягує перше числове значення та конвертує у float.
    Повертає 0.0, якщо не вдається знайти число.
    """
    try:
        # Видаляємо всі символи крім цифр, крапок та ком
        cleaned = re.sub(r'[^\d.,]', '', raw_score.replace('–', '').replace('-', ''))
        # Замінюємо коми на крапки
        cleaned = cleaned.replace(',', '.')
        # Знаходимо перше число (може бути з десятковою частиною)
        match = re.search(r'\d+\.?\d*', cleaned)
        if match:
            return float(match.group(0))
        return 0.0
    except Exception as e:
        log_error(e, f"Error cleaning score: {raw_score}")
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


async def fetch_driver(url: str, chrome_options: Options, tg_id: int):
    """Створює та налаштовує драйвер Chrome"""
    log_parsing_step(tg_id, "DRIVER_INIT", "Creating Chrome driver")
    try:
        driver = await asyncio.to_thread(webdriver.Chrome, options=chrome_options)
        log_parsing_step(tg_id, "DRIVER_READY", "Chrome driver created successfully")

        log_parsing_step(tg_id, "PAGE_LOAD", f"Loading URL: {url}")
        await asyncio.to_thread(driver.get, url)
        await asyncio.to_thread(time.sleep, 2)
        log_parsing_step(tg_id, "PAGE_LOADED", "Page loaded successfully")

        return driver
    except Exception as e:
        log_error(e, f"Error creating/fetching driver for user {tg_id}")
        raise


async def click_all_details(driver, tg_id: int):
    """Клікає на кнопку 'Завантажити ще'."""
    log_parsing_step(tg_id, "EXPAND_DETAILS", "Starting to expand all details")
    click_count = 0

    while True:
        elements = await asyncio.to_thread(driver.find_elements, By.CLASS_NAME, "detail-link")
        if not elements:
            log_parsing_step(tg_id, "EXPAND_DETAILS", f"No more detail links found, clicked {click_count} times")
            break

        clicked = False
        for el in elements:
            if el.is_displayed():
                await asyncio.to_thread(driver.execute_script, "arguments[0].click();", el)
                await asyncio.to_thread(time.sleep, 1)
                clicked = True
                click_count += 1

        if not clicked:
            log_parsing_step(tg_id, "EXPAND_DETAILS", f"Finished expanding details, total clicks: {click_count}")
            break


async def parse_rows(driver, tg_id: int) -> list[dict]:
    """Парсить дані з таблиці на сторінці."""
    log_parsing_step(tg_id, "PARSE_ROWS", "Starting to parse table rows")

    html = await asyncio.to_thread(lambda: driver.page_source)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='rwd-table')

    if not table:
        log_parsing_step(tg_id, "PARSE_ROWS", "No table found on page")
        return []

    rows = table.find_all('tr')[1:]  # Пропускаємо заголовок
    log_parsing_step(tg_id, "PARSE_ROWS", f"Found {len(rows)} rows to parse")

    results = []
    skipped_rows = 0
    invalid_data_rows = 0

    for idx, row in enumerate(rows, start=1):
        cells = [td.get_text(strip=True) for td in row.find_all('td')]

        if len(cells) < 9:
            log_parsing_step(tg_id, "PARSE_ROW_ERROR", f"Row {idx}: insufficient data ({len(cells)} cells)")
            invalid_data_rows += 1
            continue

        raw_score = cells[4]
        score = clean_score(raw_score)

        try:
            priority = int(cells[3])
        except ValueError:
            priority = 0
            log_parsing_step(tg_id, "PARSE_ROW_WARNING", f"Row {idx}: invalid priority value '{cells[3]}', using 0")

        # Перевіряємо чи це контрактна заявка
        if cells[8].upper() == 'К':
            skipped_rows += 1
            continue

        # Перевірка статусу
        if not is_valid_status(cells[2]):
            skipped_rows += 1
            continue

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

    log_parsing_step(tg_id, "PARSE_ROWS_COMPLETE",
                    f"Parsed {len(results)} valid rows, skipped {skipped_rows} invalid rows, {invalid_data_rows} rows with insufficient data")
    return results


async def parser(url: str, tg_id: int):
    """Працює з сторінкою, обробляє дані і зберігає їх у базі даних."""
    start_time = time.time()
    log_parsing_action(tg_id, "PARSING_STARTED", f"Starting parsing process", url)

    try:
        # Оновлюємо лічильник активів для звичайних користувачів
        if tg_id not in ADMIN_ID:
            await rq.update_user_activates(tg_id)
            log_parsing_step(tg_id, "ACTIVATES_UPDATED", "User activates counter updated")

        # Налаштовуємо Chrome
        user_data_dir = tempfile.mkdtemp(prefix=f"chromium_{tg_id}")
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--log-level=3")

        log_parsing_step(tg_id, "CHROME_SETUP", f"Chrome options configured, temp dir: {user_data_dir}")

        # Створюємо драйвер та завантажуємо сторінку
        driver = await fetch_driver(url, chrome_options, tg_id)

        try:
            # Очищаємо старі дані користувача
            log_parsing_step(tg_id, "CLEAR_DATA", "Clearing old user data")
            await rq.clear_user_data(tg_id)

            # Розгортає всі деталі
            await click_all_details(driver, tg_id)

            # Парсимо рядки
            rows = await parse_rows(driver, tg_id)

            if not rows:
                log_parsing_action(tg_id, "PARSING_FAILED", "No data found on page", url)
                return "Error"

            # Обробка даних
            log_parsing_step(tg_id, "PROCESS_DATA", f"Processing {len(rows)} rows")
            new_user_data = []
            competitors_count = 0
            non_competitors_count = 0

            for row in rows:
                # Відкидає контрактні заявки (тип 'К')
                if row['app_type'].upper() == 'К':
                    continue

                # Фільтрація по статусу
                if not is_valid_status(row['status']):
                    continue

                # Визначає чи є конкурент
                competitor = is_competitor(
                    row['score'], row['priority'], row['quota'], row['coefficient'], tg_id
                )

                if competitor:
                    competitors_count += 1
                else:
                    non_competitors_count += 1

                # Генерує посилання
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

            log_parsing_step(tg_id, "DATA_PROCESSED",
                           f"Processed data: {len(new_user_data)} total, {competitors_count} competitors, {non_competitors_count} non-competitors")

            # Оновлюється лічильник правильних активів для звичайних користувачів
            if tg_id not in ADMIN_ID:
                await rq.update_user_right_activates(tg_id)
                log_parsing_step(tg_id, "RIGHT_ACTIVATES_UPDATED", "User right activates counter updated")

            # Зберігає дані в базу
            log_parsing_step(tg_id, "SAVE_DATA", f"Saving {len(new_user_data)} records to database")
            await rq.set_user_data(tg_id=tg_id, new_user_data=new_user_data)

            # Логує успішне завершення
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            log_parsing_action(tg_id, "PARSING_COMPLETED",
                             f"Parsing completed successfully in {processing_time}s. "
                             f"Total records: {len(new_user_data)}, "
                             f"Competitors: {competitors_count}, "
                             f"Non-competitors: {non_competitors_count}", url)

        finally:
            # Закривається драйвер
            log_parsing_step(tg_id, "DRIVER_CLEANUP", "Closing Chrome driver")
            await asyncio.to_thread(driver.quit)

    except Exception as e:
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        log_error(e, f"Parsing failed for user {tg_id} after {processing_time}s. URL: {url}")
        log_parsing_action(tg_id, "PARSING_FAILED", f"Parsing failed after {processing_time}s: {str(e)}", url)
        raise
