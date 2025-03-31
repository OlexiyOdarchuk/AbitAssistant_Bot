def generate_link(name:str) -> str:
    """Генерує посилання на абітурієнта на сайті abit-poisk.org

    Args:
        name (str): Прізвище і ініціали(або ім'я і по-батькові) абітурієнта

    Returns:
        str: Посилання на сайт abit-poisk.org
    """
    parts = name.split() # ім'я конфертується в масив 
    if len(parts) < 2: # Якщо строк в масиві менше ніж 2
        return "Помилка: Неправильно введене ім'я!!!"
    surname = parts[0] # Прізвище це 0 елемент масиву
    first_initial = parts[1][0] # Перший ініціал це 0 елемент 1 елемента в масиві
    if len(parts) > 2: # Якщо строк в масиві більше ніж 2
        middle_initial = parts[2][0] # другий ініціал це 0 елемент 2 елемента в масиві
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}+{middle_initial}" # Повертає посилання, яке формується з повного прізвища і 2 ініціалів
    else: # Інакше
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}" # Повертає посилання, яке формується з повного прізвища і 1 ініціала 