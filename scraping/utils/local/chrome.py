from selenium import webdriver
from pprint import pprint
import os

class chrome ():

    def __init__(self,basedir):
        self.basedir = basedir

    def driver(self):
        print('ato _____')
        print(self.basedir)
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--no-sandbox")
        # driver = webdriver.Chrome(executable_path="C:\\Program Files\\Chromedriver\\Chromedriver.exe",chrome_options=chrome_options)
        prefs = {
            "download.default_directory" : "D:\\Perso",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
            }
        chrome_options.add_experimental_option("prefs",prefs)
        driver =  webdriver.Chrome(executable_path="C:\\Program Files\\Chromedriver\\Chromedriver.exe", chrome_options=chrome_options)

        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': "D:\\Perso"}}
        command_result = driver.execute("send_command", params)
        pprint(command_result)

        return driver