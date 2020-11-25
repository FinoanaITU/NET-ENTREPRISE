import sys

from selenium.common.exceptions import NoSuchElementException

class utilFunctions():
    
    def get_el_by_xpath(driver,xpath):
        return driver.find_element_by_xpath(xpath)

    def get_el_by_tag_name(driver,tag):
        return driver.find_element_by_tag_name(tag)

    def progress(count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] ...%s\r' % (bar, status))
        sys.stdout.flush()

    def click_element(self,driver, xpath):
        self.get_el_by_xpath(driver,xpath).click()

    def get_element_table(driver,BeautifulSoup,idTable,classHTML):
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        element_table = soup.find(
            'table', attrs={classHTML: idTable})

        return element_table

    def script_link(tag,textContent):
        script = "var listLienPage = document.querySelectorAll('"+tag+"'); listLienPage.forEach(function(element) {if (element.textContent ==='" + \
            textContent+"') {element.click()}})"

        return script

    def script_include(tag,textContent):
        script = "var listLienPage = document.querySelectorAll('"+tag+"'); listLienPage.forEach(function(element) {if (element.textContent.includes('" + \
            textContent+"')) {element.click()}})"
        return script
        
    def find_exist(driver,xpath):
        try:
            driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
