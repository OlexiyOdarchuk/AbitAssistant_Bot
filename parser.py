from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

def parser(url:str, file_name:str) -> str:
    """Парсить рейтинговий список абітурієнтів по спеціальності з сайту vstup.osvita.ua в txt файл з назвою користувача та повертає його шлях

    Args:
        url (str): Посилання на рейтинговий список
        file_name (str): Назва майбутнього файлу, виходячи з інформації про користувача (Default: ID)

    Returns:
        str: Абсолютний шлях до файлу з рейтинговим списком
    """
    chrome_options = Options() # Створив змінну з опціями драйвера
    chrome_options.add_argument("--headless") # Додаю опції драйверу
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options) # Задав опції для драйвера, щоб він не відображався як браузер і не займав GPU
    driver.get(url) # Запустив драйвер з url від виклику функції

    more_button = driver.find_element(By.CLASS_NAME, "detail-link") #Пошук кнопки, щоб побачити більше абітурієнтів

    while more_button.value_of_css_property("visibility") != "hidden": #Якщо в кнопки немає значення css "visibility: hidden"
        driver.execute_script("arguments[0].click();", more_button) # Натискати на кнопку "Завантажити ще" за допомогою JS
        time.sleep(1) # Чекати 1 секунду, щоб все прогрузилося 
   
    write_file = open(f'{file_name}.txt', 'w') # Створення або вдкриття файлу користувача 
    write_file.write(driver.find_element(By.CLASS_NAME, "rwd-table").text) # Запис або перезапис в цей файл таблиці абітурієнтів
    write_file.close() # Закриття файлу
    
    driver.quit() # Вихід з драйвера(браузера)

    return os.path.abspath(write_file.name) # Повертає абсолютний шлях до файлу, який пізніше буде використовуватися