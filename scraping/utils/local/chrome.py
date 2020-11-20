from selenium import webdriver
import os

class chrome ():

    def driver():
        print('ato _____')
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--no-sandbox")
        # driver = webdriver.Chrome(executable_path="C:\\Program Files\\Chromedriver\\Chromedriver.exe",chrome_options=chrome_options)
        driver = webdriver.Chrome(executable_path="C:\\Program Files\\Chromedriver\\Chromedriver.exe")

        return driver
