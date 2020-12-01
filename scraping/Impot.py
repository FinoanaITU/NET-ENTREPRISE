import re
from typing import List
from bs4 import BeautifulSoup, element
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, UnexpectedAlertPresentException

from selenium.webdriver.remote.webelement import WebElement
from .netLog import NetLog 
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .utils.utilFunctions import utilFunctions
import time

class Impot:

    def __init__(self,driver):
        self.driver = driver
        self.wait = ui.WebDriverWait(self.driver, 5000)
        self.dejaOpenTab = []

    def wait_located_xpath(self,xpath):
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def wait_located_All_xpath(self,xpath):
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))

    def wait_click_xpath(self,xpath):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def connnect(self,url,email,password):
        NetLog.connection_execut(self.driver,url)
        self.wait_located_All_xpath('//*[@id="proPriv"]')
        utilFunctions.click_element(utilFunctions,self.driver,'//*[@id="proPriv"]')
        self.wait_located_All_xpath('//*[@id="lmdp"]')
        utilFunctions.get_el_by_xpath(self.driver,'//*[@id="ident"]').send_keys(email)
        utilFunctions.get_el_by_xpath(self.driver,'//*[@id="mdp"]').send_keys(password)
        utilFunctions.get_el_by_xpath(self.driver,'//*[@id="valider"]').click()
        
        self.wait.until(EC.url_contains('https://cfspro.impots.gouv.fr/mire/accueil.do'))
        return True
    
    def choix_dossier(self, siren):
        #click choix dossier
        self.wait_located_All_xpath('//*[@id="LayerMenuPrincipal"]/li[1]/ul/li[1]/a')
        script = utilFunctions.script_include('a','Choisir un dossier')
        self.driver.execute_script(str(script), None)
        #get all input to fill
        self.wait_located_All_xpath('//*[@id="ins_contenu"]/table/tbody/tr[2]/td/form')
        i = 0
        for element in siren:
            input = utilFunctions.get_el_by_xpath(self.driver,'//*[@id="siren'+str(i)+'"]')
            input.send_keys(element)
            i += 1
        self.wait_click_xpath('//*[@id="chooserep"]/span/input')
        time.sleep(1)
        try:
            utilFunctions.click_element(utilFunctions, self.driver,'//*[@id="chooserep"]/span/input')
        except ElementClickInterceptedException:
            time.sleep(2)
            utilFunctions.click_element(utilFunctions, self.driver,'//*[@id="chooserep"]/span/input')
    
    def compte_fiscale(self):
        self.wait_click_xpath('//*[@id="mes_serv"]/div[2]/ul/li[1]/a')
        try:
            utilFunctions.click_element(utilFunctions, self.driver,'//*[@id="mes_serv"]/div[2]/ul/li[1]/a')
        except ElementClickInterceptedException:
            time.sleep(2)
            self.compte_fiscale()
            
        time.sleep(2)
        self.dejaOpenTab = utilFunctions.switch_one_tab(self.driver, self.dejaOpenTab)
        #wait compte fiscale afficher
        self.wait_located_xpath('//*[@id="chemin_de_fer"]/a')
        script = utilFunctions.script_include('a','Attestation de Régularité Fiscale')
        self.driver.execute_script(str(script), None)
        #
        self.wait_located_All_xpath('//*[@id="Formulaire"]')
        
        try:
            self.click_radio()
        except UnexpectedAlertPresentException:
            time.sleep(3)
            self.click_radio()

        time.sleep(2)
        self.wait_located_All_xpath('//*[@id="attestation"]')
        
        return True

    def click_radio(self):
        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="membreIS_groupe_non"]')
        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="membreTVA_groupe_non"]')
        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="boutons"]/table[2]/tbody/tr/td[2]/span')

    def imprimer(self,siren):
        script = utilFunctions.script_include('a','impression')
        self.driver.execute_script(str(script), None)
        All_tab = utilFunctions.switch_one_tab(self.driver, self.dejaOpenTab)
        time.sleep(2)
        self.check_table(siren)

    def check_table(self, siren):
        element_table = utilFunctions.get_element_table(self.driver, BeautifulSoup, 'tableau','class')
        all_doc = element_table.findAll('tr')
        sirenText = str(siren)
        doc_down = False
        link = None
        for doc in all_doc:
            if link is not None:
                break
            else:
                tag = doc.findAll('td')
                print('ATO 1----------------------------')
                for text in tag:
                    content = text.contents
                    print('ATO 2----------------------------')
                    if sirenText in content[0]:
                        img = doc.find('img')
                        print('ATO 3----------------------------')
                        if self.check_doc_ready(img['src']):
                            link = doc.find('a', href=True)
                            break
                        else:
                            #lencer recursive
                            print('RECURSIVE ------')
                            time.sleep(5)
                            self.check_table(siren)
        print('lien-----------------------------------------')
        print(str(link['href']))
        try:
            self.driver.find_element_by_xpath('//a[@href="'+link['href']+'"]').click()
        except NoSuchElementException:
            pass
                    
    
    def check_doc_ready(self,imgName):
        check = re.search('termine', imgName)
        if check is not None:
            return True
        else:
            return False