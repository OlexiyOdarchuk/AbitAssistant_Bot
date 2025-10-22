import asyncio
import aiohttp
import aiofiles
import json
import os
from collections import defaultdict
from config import API_URL
from app.services.logger import log_parsing_action, log_parsing_step, log_error

output_dir = "jsons"
os.makedirs(output_dir, exist_ok=True)


async def create_payload(url: str, last: int, tg_id: int) -> dict:
    """Функція, що генерує словник, який пізніше буде передаватися як запит для отримання посилання на json

    Args:
        url (str): Посилання спеціальності, яку потрібно парсити
        last (int): Абітурієнт від якого починати парс

    Returns:
        dict: Повертає словник, який є параметрами запиту
    """
    try:
        data = url.split("/")
        while not (data[-1]):
            data.pop(-1)
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


async def get_url_json(sess: aiohttp.ClientSession, payload: dict, tg_id: int) -> str:
    """Отримує посилання на Json з якого пізніше будуть отримуватися данні про абітурієнтів

    Args:
        sess (aiohttp.ClientSession): Сесія aiohttp
        payload (dict): Словник з параметрами запиту
        tg_id (int): Телеграм ID користувача

    Returns:
        str: Посилання на json
    """
    try:
        async with sess.post(API_URL, data=payload, allow_redirects=True) as resp:
            try:
                j = await resp.json(content_type=None)
                log_parsing_step(tg_id, "URL JSON received")
            except aiohttp.ContentTypeError:
                text = await resp.text()
                log_parsing_step(tg_id, "ContentTypeError", details=text)
                j = None

        if j is None or not j.get("url"):
            log_error("No URL", f"[User {tg_id}] Error getting URL JSON")
            return None
        return j.get("url")
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error getting URL JSON")
        return None


async def read_json(file_name: str, tg_id: int) -> dict:
    """Зчитує json файл і повертає його вміст

    Args:
        file_name (str): ім'я файлу, яке потрібно зчитати

    Returns:
        dict: вміст json файлу
    """
    try:
        async with aiofiles.open(file_name, mode="r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)
            log_parsing_step(tg_id, f"Read JSON file {file_name}")
            return data
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error reading JSON file {file_name}")
        return {}


async def write_json(file_name: str, data: dict, tg_id: int):
    """Записує json файл вмістом

    Args:
        file_name (str): ім'я файлу
        data (dict): вміст
    """
    try:
        async with aiofiles.open(file_name, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
            log_parsing_step(tg_id, f"Written JSON file {file_name}")
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error writing JSON file {file_name}")


async def merge(json_files: list, tg_id: int):
    """Об'єднує всі json файли з списку в 1

    Args:
        json_files (list): список файлів для об'єднання
        tg_id (int): телеграм ID користувача, який надіслав запит
    """
    try:
        merged = defaultdict(list)
        tasks = [read_json(f, tg_id) for f in json_files]
        results = await asyncio.gather(*tasks)

        for data in results:
            for key, value in data.items():
                if isinstance(value, list):
                    merged[key].extend(value)

                elif isinstance(value, dict):
                    if merged[key] and isinstance(merged[key][-1], dict):
                        merged[key][-1].update(value)

                    else:
                        merged[key].append(value)

                elif value is not None:
                    merged[key].append(value)

        merged_dict = dict(merged)
        output_file = os.path.join(output_dir, f"{tg_id}.json")
        await write_json(output_file, merged_dict, tg_id)

        for f in json_files:
            os.remove(f)
        log_parsing_action(tg_id, f"Merged {len(json_files)} files into {output_file}")
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error merging JSON files")


async def parse(url: str, tg_id: int):
    """Парсить дані з сайту

    Args:
        url (str): посилання на сайт, який треба пропарсити
        tg_id (int): Телеграм ID користувача, що надіслав запит
    """
    try:
        log_parsing_action(tg_id, f"Started parsing for URL: {url}")
        count_abits = 0
        count_files = 1
        json_files = []

        async with aiohttp.ClientSession() as session:
            while True:
                payload = await create_payload(url, count_abits, tg_id)
                data_url = await get_url_json(session, payload, tg_id)
                if data_url is None:
                    break

                async with session.get(data_url) as resp:
                    data = await resp.json()

                if not data.get("requests"):
                    break

                file_name = os.path.join(output_dir, f"{tg_id}_{count_files}.json")
                async with aiofiles.open(file_name, mode="w", encoding="utf-8") as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=4))
                log_parsing_step(tg_id, f"Saved JSON file {file_name}")

                json_files.append(file_name)
                count_abits += 500
                count_files += 1

        await merge(json_files, tg_id)
        log_parsing_action(tg_id, "Parsing completed successfully")
    except Exception as e:
        log_error(e, f"[User {tg_id}] Error during parsing")
