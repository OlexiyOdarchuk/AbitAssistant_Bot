import aiohttp
from config import API_URL
from app.services.logger import log_parsing_action, log_parsing_step, log_error


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
            "last": str(last[0]),
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
        async with session.post(API_URL, data=payload, allow_redirects=True) as resp:
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


async def parser(
    url: str,
    tg_id: int,
    last: list,
    session: aiohttp.ClientSession,
) -> dict:  # Оскільки не можна написати &last як в С++, треба викручуватися) вибрав писати через ліст, бо він змінний
    """Парсить дані з сайту і повертає значення в вигляді dict

    Args:
        url (str): посилання на сайт, який треба пропарсити
        tg_id (int): Телеграм ID користувача, що надіслав запит
        last (list): Список з 1 елементом, в якому номер останнього спаршеного обітурієнта
        session (aiohttp.ClientSession): Сесія aiohttp. Передається як аргумент, щоб не забанив сайт за часті запити
    Returns:
        dict: спаршені дані
    """
    try:
        log_parsing_action(tg_id, f"Started parsing for URL: {url}")
        payload = await create_payload(url, last, tg_id)
        data_url = await get_url_json(session, payload, tg_id)
        if data_url is None:
            log_error("DATA_URL NONE", "Немає нічо")
            return None

        async with session.get(data_url) as resp:
            data = await resp.json()

        if data is None or not data.get("requests"):
            return None

        last[0] += 500

        log_parsing_action(tg_id, "Parsing completed successfully")

        return data

    except Exception as e:
        log_error(e, f"[User {tg_id}] Error during parsing")
