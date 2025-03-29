from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def parser(url:str, user_id:str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    more = driver.find_element(By.CLASS_NAME, "detail-link")
    while more.value_of_css_property("visibility") != "hidden":
        driver.execute_script("arguments[0].click();", more)
        time.sleep(0.1)
        more = driver.find_element(By.CLASS_NAME, "detail-link")

    time.sleep(0.5)
    name = driver.find_element(By.CLASS_NAME, "rwd-table").text
    driver.quit()
    write = open(f'{user_id}.txt', 'w')
    write.write(name)
    write.close()
    file_name = f'{user_id}.txt'
    return(file_name)