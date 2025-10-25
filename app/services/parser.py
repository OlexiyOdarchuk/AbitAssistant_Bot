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

import aiohttp
from bs4 import BeautifulSoup
import re
import json
from config import API_URL
from app.services.logger import log_parsing_action, log_parsing_step, log_error

PAGE_SIZE = 500


async def create_payload(url: str, last: int, tg_id: int) -> dict:
    """Функція, що генерує словник, який пізніше буде передаватися як запит для отримання посилання на json

    Args:
        url (str): Посилання спеціальності, яку потрібно парсити
        last (int): Абітурієнт від якого починати парс

    Returns:
        dict: Повертає словник, який є параметрами запиту
    """
    try:
        data = url.strip("/").split("/")
        sid = data[-1]
        uid = data[-2]
        y = data[-4][1:]
        payload = {
            "action": "requests",
            "y": y,
            "sid": sid,
            "uid": uid,
            "last": str(last),
        }
        log_parsing_step(tg_id, "Payload created", details=str(payload))
        return payload
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error creating payload")
        raise


async def get_url_json(
    session: aiohttp.ClientSession, payload: dict, tg_id: int
) -> str:
    """Отримує посилання на Json з якого пізніше будуть отримуватися данні про абітурієнтів

    Args:
        sess (aiohttp.ClientSession): Сесія aiohttp
        payload (dict): Словник з параметрами запиту
        tg_id (int): Телеграм ID користувача

    Returns:
        str: Посилання на json
    """
    try:
        for i in range(2):  # З першого разу запит чомусь нічого не повертає
            async with session.post(
                API_URL, data=payload, allow_redirects=True
            ) as resp:
                try:
                    json_url = await resp.json(content_type=None)
                    log_parsing_step(tg_id, "URL JSON received")
                except aiohttp.ContentTypeError:
                    text = await resp.text()
                    log_parsing_step(tg_id, "ContentTypeError", details=text)
                    json_url = None

        if json_url is None or not json_url.get("url"):
            log_error("No URL", f"[User {tg_id}] Error getting URL JSON")
            return None
        return json_url.get("url")
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error getting URL JSON")
        return None


async def fetch_html(url: str, session, tg_id: int) -> str:
    """Парсить з сайту html і повертає його як текст"""
    try:
        log_parsing_step(tg_id, "Fetching HTML", details=f"URL: {url}")
        async with session.get(url) as resp:
            html = await resp.text()
        log_parsing_step(tg_id, "HTML fetched successfully")
        return html
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error fetching HTML from {url}")
        return ""


def parse_js_variable(js_text: str, var_name: str, tg_id: int):
    """Витягує JS-обʼєкт або масив і конвертує dict/list."""
    try:
        log_parsing_step(tg_id, f"Parsing JS variable: {var_name}")
        pattern = re.compile(
            rf"{re.escape(var_name)}\s*=\s*(\{{.*?\}}|\[.*?\]);", re.DOTALL
        )
        match = pattern.search(js_text)
        if match:
            js_object = match.group(1)
            js_object = re.sub(r"//.*?\n|/\*.*?\*/", "", js_object, flags=re.S)
            js_object = js_object.replace("'", '"')
            parsed = json.loads(js_object)
            log_parsing_step(tg_id, f"JS variable {var_name} parsed successfully")
            return parsed
        log_parsing_step(tg_id, f"JS variable {var_name} not found")
        return None
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error parsing JS variable {var_name}")
        return None


async def parse_program_data(url: str, session, tg_id: int) -> dict:
    log_parsing_action(tg_id, "Parsing program data", details=f"URL: {url}")
    try:
        html_text = await fetch_html(url, session, tg_id)
        soup = BeautifulSoup(html_text, "html.parser")
        result = {}

        h2_tag = soup.select_one(".page-vnz-detail-title h2")
        if h2_tag:
            result["university_name"] = h2_tag.get_text(strip=True)
            log_parsing_step(
                tg_id, "University name parsed", details=result["university_name"]
            )

        h1_tag = soup.select_one(".page-vnz-detail-title h1")
        if h1_tag:
            text = h1_tag.get_text(" ", strip=True)
            result["program_name"] = re.search(
                r"Освітня програма: (.+?)\.", text
            ).group(1)
            result["spec_code"] = re.search(r"Спеціальність: (\S+)\.", text).group(1)
            log_parsing_step(
                tg_id,
                "Program name and spec code parsed",
                details=str(result["program_name"] + " | " + result["spec_code"]),
            )

        # Основні дані програми
        program_block = soup.select_one(".block-pro-vnz .table-of-specs-item")
        if program_block:
            main_data = {}
            for b_tag in program_block.find_all("b"):
                key = b_tag.text.replace(":", "").strip()
                next_elem = b_tag.next_sibling
                if next_elem and getattr(next_elem, "text", None):
                    value = next_elem.text.strip()
                else:
                    value = next_elem.strip() if next_elem else ""
                main_data[key] = value
            result["program_info"] = main_data
            log_parsing_step(tg_id, "Main program info parsed", details=str(main_data))

        # Статистика спеціальності

        # stats_table = soup.select_one(".stats-vnz-table")
        # stats = {}
        # if stats_table:
        #   for tr in stats_table.find_all("tr"):
        #       cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        #       if len(cols) == 2:
        #           stats[cols[0]] = cols[1]
        # result["stats"] = stats

        # Ліцензований обсяг
        volume_block = None
        for block in soup.select(".block-pro-vnz"):
            if "Ліцензований обсяг прийому" in block.get_text():
                volume_block = block
                break
        if volume_block:
            volume_data = {}
            for b_tag in volume_block.find_all("b"):
                key = b_tag.previous_sibling.strip().replace(":", "")
                volume_data[key] = b_tag.text.strip()
            result["volume"] = volume_data
            log_parsing_step(tg_id, "Volume data parsed", details=str(volume_data))

        # Парсинг JS-змінних
        scripts = soup.find_all("script")
        js_text = "\n".join(script.string or "" for script in scripts)

        result["statuses"] = parse_js_variable(js_text, "statuses", tg_id)
        result["rec_types"] = parse_js_variable(js_text, "rec_types", tg_id)
        result["subjects_js"] = parse_js_variable(js_text, "subjects", tg_id)

        log_parsing_step(tg_id, "All JS variables parsed")

        return result
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error parsing program data")
        return {}


async def parser(url: str, tg_id: int) -> dict:
    """Парсить дані з сайту і повертає один великий словник"""
    try:
        log_parsing_action(tg_id, f"Started parsing for URL: {url}")
        last = 0

        async with aiohttp.ClientSession() as session:
            data = await parse_program_data(url, session, tg_id)  # Статична інформація

            requests_list = []
            requests_subjects_dict = {}
            while True:
                payload = await create_payload(url, last, tg_id)
                data_url = await get_url_json(session, payload, tg_id)
                if not data_url:
                    break

                async with session.get(data_url) as resp:
                    resp_data = await resp.json()

                if not resp_data.get("requests"):
                    break

                requests_list.extend(resp_data.get("requests"))
                for k, v in resp_data.get("requests_subjects", {}).items():
                    requests_subjects_dict[k] = v

                last += PAGE_SIZE

            data["requests"] = requests_list
            data["requests_subjects"] = requests_subjects_dict
            log_parsing_action(tg_id, "Parsing completed successfully")
            return data

    except Exception as e:
        log_error(e, f"[User {tg_id}] Error during parsing")
        return None
