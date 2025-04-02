import asyncio

async def generate_link(name: str) -> str:
    """Асинхронно генерує посилання на абітурієнта на сайті abit-poisk.org

    Args:
        name (str): Прізвище і ініціали (або ім'я і по-батькові) абітурієнта

    Returns:
        str: Посилання на сайт abit-poisk.org
    """
    await asyncio.sleep(0)
    parts = name.split() 
    if len(parts) < 2: 
        return "Помилка: Неправильно введене ім'я!!!"
    surname = parts[0] 
    first_initial = parts[1][0] 
    if len(parts) > 2:  
        middle_initial = parts[2][0] 
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}+{middle_initial}" 
    elif len(parts) == 2:
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}" 
    else:
        return ValueError