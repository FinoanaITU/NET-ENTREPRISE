from selenium import webdriver
import os

class chrome ():

    def __init__(self,basedir):
        self.basedir = basedir

    def driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        print(self.basedir+"/files")
        prefs = {"download.default_directory" : self.basedir+"/files"}
        chrome_options.add_experimental_option("prefs",prefs)
        return  webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        
