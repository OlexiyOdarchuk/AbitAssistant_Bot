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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

async def fetch_page(url: str, chrome_options: Options):
    """Запускає драйвер для отримання сторінки"""
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver

async def click_more_button(driver) -> None:
    """Натискає на кнопку 'Завантажити ще' поки вона видна"""
    more_button = driver.find_element(By.CLASS_NAME, "detail-link")

    while more_button.value_of_css_property("visibility") != "hidden":
        driver.execute_script("arguments[0].click();", more_button)
        await asyncio.sleep(1)  # Затримка, щоб все прогрузилося

async def save_to_file(driver, file_name: str) -> str:
    """Зберігає дані в файл"""
    file_path = f'app/files/{file_name}.txt'
    with open(file_path, 'w') as write_file:
        write_file.write(driver.find_element(By.CLASS_NAME, "rwd-table").text)

    return file_path

async def parser(url: str, file_name: str) -> str:
    """Асинхронний парсер рейтингового списку абітурієнтів"""

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--no-sandbox")

    # Отримуємо сторінку (зараз асинхронно)
    driver = await fetch_page(url, chrome_options)

    # Натискаємо на кнопку "Завантажити ще" (асинхронно)
    await click_more_button(driver)

    # Зберігаємо дані в файл
    file_path = await save_to_file(driver, file_name)

    driver.quit()

    return os.path.abspath(file_path)
