import aiohttp
from bs4 import BeautifulSoup
from config import ABIT_POISK_API_URL


async def fetch_applicant_data(name: str) -> list[dict]:
    """Приймає ім'я людини і повертає інформацію про цю людину з abit-poisk

    Args:
        name (str): ім'я абітурієнта

    Returns:
        list[dict]: всі його заяви і інформація про них
    """
    connector = aiohttp.TCPConnector(ssl=False)  # вимикаємо перевірку SSL
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(
            ABIT_POISK_API_URL,
            data={"search": name},
        ) as resp:
            json_data = await resp.json()

    html = json_data.get("html", "")
    if not html:
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

    return result
