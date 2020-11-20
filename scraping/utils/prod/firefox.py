from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

import os

class firefox():

    def __init__(self, app):
        self.app = app

    def driver(self):
        binary = FirefoxBinary(os.environ.get("FIREFOX_BIN"))
        options = Options()
        options.set_headless(headless=True)
        options.binary = binary

        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = False

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference('browser.download.dir', self.app.config['PATH_FILE'])
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                        " application/pdf, attachment/pdf")
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        # fp.set_preference("browser.preferences.instantApply", True)
        # fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
        #                   "text/plain, application/octet-stream, application/pdf, attachment/pdf, application/binary, text/csv, application/csv, application/excel, text/comma-separated-values, text/xml, application/xml")
        # fp.set_preference("browser.helperApps.alwaysAsk.force", False)
        fp.set_preference("pdfjs.disabled", True)

        fp.set_preference("plugin.scan.Acrobat", "99.0")
        fp.set_preference("plugin.scan.plid.all", False)

        

        # with Display():
        driver = webdriver.Firefox(executable_path=os.environ.get("GECKODRIVER_PATH"), firefox_profile=fp, firefox_options=options, capabilities=cap)

        return driver