from selenium import webdriver
import os

class chrome ():

    def __init__(self,basedir):
        self.basedir = basedir

    def driver(self):
        print('ato _____')
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--no-sandbox")
        # driver = webdriver.Chrome(executable_path="C:\\Program Files\\Chromedriver\\Chromedriver.exe",chrome_options=chrome_options)
        prefs = {
            "download.default_directory" : self.basedir+"\\files",
             "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
            }
        chrome_options.add_experimental_option("prefs",prefs)
        return webdriver.Chrome(executable_path="C:\\Program Files\\Chromedriver\\Chromedriver.exe", chrome_options=chrome_options)