import aiohttp
from bs4 import BeautifulSoup
from config import ABIT_POISK_API_URL
from app.services.logger import log_error, log_parsing_step


async def fetch_applicant_data(name: str, tg_id: int = 0) -> list[dict]:
    """Приймає ім'я людини і повертає інформацію про цю людину з abit-poisk

    Args:
        name (str): ім'я абітурієнта
        tg_id (int): Telegram ID користувача для логування

    Returns:
        list[dict]: всі його заяви і інформація про них (порожній список якщо помилка)
    """
    try:
        log_parsing_step(tg_id, f"Fetching abit-poisk data for {name}")
        connector = aiohttp.TCPConnector(ssl=False)  # вимикаємо перевірку SSL
        async with aiohttp.ClientSession(
            connector=connector, timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.post(
                ABIT_POISK_API_URL,
                data={"search": name},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log_error(
                        f"abit-poisk returned {resp.status}", f"[User {tg_id}] {name}"
                    )
                    return []

                json_data = await resp.json()

        html = json_data.get("html", "")
        if not html:
            log_parsing_step(tg_id, f"No HTML data for {name}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.table tbody tr")

        result = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 14:
                continue

            entry = {
                "degree": cells[0].get_text(strip=True),  # ОКР
                "full_name": cells[1].get_text(strip=True),  # ПІБ
                "status": cells[2].get_text(strip=True),  # Статус заяви
                "ranking_number": cells[3].get_text(strip=True),  # № у списку
                "priority": cells[4].get_text(strip=True),  # Пріоритет
                "total_score": cells[6].get_text(strip=True),  # Заг. бал
                "education_avg": cells[7].get_text(strip=True),  # СБО
                "university": cells[9].get_text(strip=True),  # ВНЗ
                "faculty": cells[10].get_text(strip=True),  # Факультет
                "specialty": cells[11].get_text(strip=True),  # Спец.
                "quota": cells[12].get_text(strip=True),  # Квота
                "original_docs_submitted": cells[13].get_text(strip=True),  # Оригінали
            }
            result.append(entry)

        log_parsing_step(tg_id, f"Found {len(result)} applications for {name}")
        return result
    except aiohttp.ClientConnectorError as e:
        log_error(
            e, f"[User {tg_id}] Network error contacting abit-poisk: {str(e)[:100]}"
        )
        return []
    except aiohttp.ClientSSLError as e:
        log_error(e, f"[User {tg_id}] SSL error with abit-poisk: {str(e)[:100]}")
        return []
    except aiohttp.ClientError as e:
        log_error(e, f"[User {tg_id}] aiohttp error: {str(e)[:100]}")
        return []
    except Exception as e:
        log_error(e, f"[User {tg_id}] Unexpected error fetching abit data for {name}")
        return []
