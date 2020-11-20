from typing import Counter
from bs4.element import Script
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from selenium.webdriver.common import service
from .utils.utilFunctions import utilFunctions
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
from bs4 import BeautifulSoup
import re


class NetLog():

    def __init__(self,driver):
        self.driver = driver
        self.wait = ui.WebDriverWait(self.driver, 5000)
        

    def run_login(self, urlPage, userNom, userPrenom, siret, password):
        self.connection_execut(urlPage)
        self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="masthead"]/div[2]/div/div')))
        time.sleep(2)
        utilFunctions.get_el_by_xpath(
            self.driver,'//*[@id="masthead"]/div[1]/div/div/div[2]/div[1]').click()
        self.fill_acompt_login(userNom, userPrenom, siret,password)

       
        try:
            utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="validButtonConnexion"]')
        except ElementClickInterceptedException:
             if utilFunctions.find_exist(self.driver,'//*[@id="cn-accept-cookie"]'):
                utilFunctions.click_element(utilFunctions, self.driver,'//*[@id="cn-accept-cookie"]')

        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="validButtonConnexion"]')

        return True
       
        

    def connection_execut(self, urlPage):
        self.driver.get(urlPage)

    def fill_acompt_login(self, userNom, userPrenom, siret, password):
        utilFunctions.get_el_by_xpath(
            self.driver, '//*[@id="j_siret"]').send_keys(siret)
        utilFunctions.get_el_by_xpath(
            self.driver, '//*[@id="j_nom"]').send_keys(userNom)
        utilFunctions.get_el_by_xpath(
            self.driver, '//*[@id="j_prenom"]').send_keys(userPrenom)
        utilFunctions.get_el_by_xpath(
            self.driver, '//*[@id="j_password"]').send_keys(password)

    def find_and_click(self, xpathElement):
        utilFunctions.click_element(
            utilFunctions, self.driver, xpathElement)
    
    def start_parcourt_to_urssaf(self):
        #click sur DUCS
        click = utilFunctions.script_include('a','DUCS')
        self.driver.execute_script(str(click), None)
        self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="AccrochageEFIEDIChoice"]')))
        time.sleep(5)
        #click sur le service EFI(variable)
        self.find_and_click(
            '/html/body/table/tbody/tr[3]/td[2]/div[6]/table/tbody/tr[1]/td[1]/form/center/a')

        self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="sirenChoice"]')))
        time.sleep(5)

        #click sur un des entreprise EFI(variable)
        self.find_and_click(
            '//*[@id="sirenChoice"]/tbody/tr[19]/td[1]/center/a')

        self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="TdBDeclaUrssaf"]')))
        time.sleep(3)

        #click sur un lien vers URSSAF(variable)
        self.find_and_click('//*[@id="TdBDeclaUrssafBody"]/tr/td[1]/a')

        self.wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '/html/body/div/div/table')))
        time.sleep(3)

        #click sur continuer
        self.find_and_click('/html/body/div/div/table/tbody/tr[9]/td/img')

    def list_services(self):
        if utilFunctions.find_exist(self.driver, '//*[@id="widget-base-de-co"]/div/div[1]') and utilFunctions.get_el_by_xpath(self.driver,'//*[@id="widget-base-de-co"]/div/div[1]').is_displayed():
            try:
                utilFunctions.get_el_by_xpath(self.driver, '//*[@id="widget-base-de-co"]/div/div[1]').click()
            except ElementNotInteractableException:
                self.list_services()
                   
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="carousel"]/div/div/div[16]')))
        #click sur DUCS
        click = utilFunctions.script_include('a','DUCS')
        self.driver.execute_script(str(click), None)

        # self.wait.until(EC.presence_of_element_located(
        #     (By.XPATH, '//*[@id="AccrochageEFIEDIChoice"]')))
        self.wait.until(
            lambda driver: utilFunctions.get_el_by_xpath(self.driver,'//*[@id="AccrochageEFIEDIChoice"]').is_displayed())
        time.sleep(2)

        element_table = utilFunctions.get_element_table(self.driver, BeautifulSoup, 'AccrochageEFIEDIChoice')
        services_lik = element_table.find_all('span', class_='label')
        services_list = []
        for service in services_lik:
            label = service.text
            titre = None
            if len(label) > 3:
                titre = label
                if titre is not None and titre != 'Services':
                    services_list.append(titre)
        self.return_acceuil()
        return services_list

    def list_entreprise(self,service):
        try:
            utilFunctions.get_el_by_xpath(self.driver, '//*[@id="widget-base-de-co"]/div/div[1]').click()
        except ElementClickInterceptedException:
            print('no')

        #click sur DUCS
        click = utilFunctions.script_include('a','DUCS')
        self.driver.execute_script(str(click), None)

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="AccrochageEFIEDIChoice"]')))
        time.sleep(2)

        #click sur services selectioner
        script = utilFunctions.script_link('a',service)
        self.driver.execute_script(str(script), None)

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="sirenChoice"]')))
        time.sleep(2)

        #get all list entreprise
        element_table = utilFunctions.get_element_table(self.driver, BeautifulSoup, 'sirenChoice')
        all_entreprise = element_table.findAll('tr')
        list_entreprise = []

        for i,entreprise in enumerate(all_entreprise):
            siren = re.search("(?<=\(')(.*)(?=\'\))", str(entreprise))
            social = re.search("(?<=\</td>\s<td>)(.*)(?=\</td></tr>)", str(entreprise))
            if siren is not None and social is not None:
                data = {
                    'siren': siren.group(0),
                    'raison_social': social.group(0)
                }
                # print(data)
                list_entreprise.append(data)
        # if len(list_entreprise) != 0:
        #     self.return_acceuil()

        return list_entreprise

    def return_acceuil(self):
        self.find_and_click('//*[@id="label_trans_RetourMenu"]')

    #document direct.
    def doc_urssaf(self,siren):
        #click siren
        script = utilFunctions.script_link('a',siren)
        self.driver.execute_script(str(script), None)

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="TdBDeclaUrssaf"]')))
        time.sleep(2)

        #find document urssaf
        element_table = utilFunctions.get_element_table(
            self.driver, BeautifulSoup, 'TdBDeclaUrssaf')
        all_doc = element_table.findAll('tr')
        list_doc = []

        for doc in all_doc:
            stringDoc = str(doc)
            text = stringDoc.replace('"', "")
            textFinal = text.replace("'", "")
            periode = re.search('(?<=\)>)(.*)(?=\<\/a><\/td>)', textFinal)
            numero = re.search('(?<!\d)\d{18}(?!\d)', str(doc))
            date_limite = re.search('(?<=contenuTableauPeriode>)(.*)(?=\<\/td><td class=contenuTableauPeriode>)', textFinal)
            if periode is not None and numero is not None and date_limite is not None:
                data = {
                    'periode':periode.group(0),
                    'numero': numero.group(0),
                    'date_limite': date_limite.group(0)
                }
                list_doc.append(data)

        utilFunctions.get_el_by_xpath(
            self.driver, '/html/body/table/tbody/tr[1]/td/table/tbody/tr/td[1]/span/a').click()
        return list_doc

    def to_urssaf(self,periode,siren):
        #click siren
        script = utilFunctions.script_link('a', siren)
        self.driver.execute_script(str(script), None)
        
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/table/tbody/tr[3]/td[2]/div[8]/table/thead/tr/th[1]/span/a')))
        time.sleep(2)

        #click periode
        script = utilFunctions.script_link('a', periode)
        self.driver.execute_script(str(script), None)
        time.sleep(5)
        # if EC.presence_of_element_located((By.XPATH, '/ html/body/div/div/table/tbody/tr[9]/td/img')):
        #     self.wait.until(EC.presence_of_element_located(
        #         (By.XPATH, '/html/body/div/div/table/tbody/tr[9]/td/img')))
        #     print('misy continue------------------------------')
        #     #click sur continuer
        #     self.find_and_click('/html/body/div/div/table/tbody/tr[9]/td/img')
        self.wait.until(EC.url_contains('www.declaration.urssaf.fr'))
        return True

    def initialise_downloadFile(self,doc_name,doc_type):
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="navbar-blue"]')))

        #entrer dans document
        script = utilFunctions.script_link('a', doc_name)
        self.driver.execute_script(str(script), None)
        print('tafa attestation click ----------')
        time.sleep(2)
        self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[3]/div[2]/section[1]/h2')))
        if utilFunctions.find_exist(self.driver,'/html/body/div[3]/div[2]/section[1]/div[3]/div[3]/div[2]/button'):
            self.execut_download(doc_type)
        else:
            utilFunctions.get_el_by_xpath(self.driver,'/html/body/div[3]/div[2]/section[1]/section/div[3]/div/button').click()
            self.initialise_downloadFile(doc_name,doc_type)
        
    def execut_download(self,doc_type):
        self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="typeAttestation"]')))

        selectType = utilFunctions.script_link('select[id="typeAttestation"]',doc_type)
        self.driver.execute_script(str(selectType))
        print(' tafa slct ----------')

        #click valider
        utilFunctions.get_el_by_xpath(
            self.driver, '/html/body/div[3]/div[2]/section[1]/div[3]/div[3]/div[2]/button').click()
        print(' tafa valider ----------')
        time.sleep(2)
        if utilFunctions.get_el_by_xpath(self.driver, '/html/body/div[3]/div[2]/section[1]/div[3]/div[9]/div').is_displayed():
            print(' click modal ----------')
            utilFunctions.get_el_by_xpath(
                self.driver, '/html/body/div[3]/div[2]/section[1]/div[3]/div[9]/div/div/div[3]/button[1]').click()
            time.sleep(5)
        print(' vita click modal ----------')
        #find all element int table
        print(' lancer down ----------')
        utilFunctions.get_el_by_xpath(self.driver,'/html/body/div[3]/div[2]/section[1]/div[3]/div[7]/div[2]/div/table/tbody/tr[1]/td[6]/a').click()
        print(' vita down ----------')     
        