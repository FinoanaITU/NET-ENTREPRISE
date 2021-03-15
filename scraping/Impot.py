import re
from typing import List
from bs4 import BeautifulSoup, element
from flask import json
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, UnexpectedAlertPresentException

from selenium.webdriver.remote.webelement import WebElement
from .netLog import NetLog 
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .utils.utilFunctions import utilFunctions
import time
import requests
from urllib3.exceptions import MaxRetryError

class Impot:

    def __init__(self,driver):
        self.driver = driver
        self.wait = ui.WebDriverWait(self.driver, 5000)
        self.dejaOpenTab = []
        self.compteurDown = 0
        self.dataDown = []

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
        if self.driver != None :
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

            return True
        else:
            time.sleep(2)
            self.choix_dossier(siren)
    
    def access_compte(self, type):
        if self.driver != None :
            self.wait_click_xpath('//*[@id="mes_serv"]/div[2]/ul/li[1]/a')
            try:
                if type == 'compte_fiscale':
                    utilFunctions.click_element(utilFunctions, self.driver,'//*[@id="mes_serv"]/div[2]/ul/li[1]/a')
                elif type == 'TVA':
                    regex = '/afficherChoisirOCFI.*action=declarer/g'
                    script = utilFunctions.script_find_lien('TVA',regex)
                    self.driver.execute_script(str(script), None)

            except ElementClickInterceptedException:
                time.sleep(2)
                self.access_compte(type)
                
            time.sleep(2)
            self.dejaOpenTab = utilFunctions.switch_one_tab(self.driver, self.dejaOpenTab)
            #wait compte fiscale afficher
            # self.wait_located_xpath('//*[@id="chemin_de_fer"]/a')
            self.wait_located_xpath('//*[@id="racine"]') if type == 'compte_fiscale' else self.wait_located_xpath('//*[@id="ins_contenu"]/form/table[1]')
            return True
        else:
            time.sleep(2)
            self.access_compte(type)


    def attestation_fiscale(self,siren):
        script = utilFunctions.script_include('a','Attestation de Régularité Fiscale')
        self.driver.execute_script(str(script), None)
        #
        self.wait_located_All_xpath('//*[@id="Formulaire"]')
        print('DEPART CLICK RADIO --------------------')
        try:
            print('TRY --------------------')
            self.click_radio()
        except UnexpectedAlertPresentException:
            alert_obj = self.driver.switch_to.alert
            alert_obj.accept()
            print('except --------------------')
            self.click_radio()
        print('TAFA --------------------')
        self.wait_located_All_xpath('//*[@id="attestation"]')
        data = self.imprimer(siren)
        return data

    def declarer_tva(self,dataFormulaire):
        utilFunctions.click_element(utilFunctions, self.driver,'//*[@id="ins_contenu"]/form/table[2]/tbody/tr/td[2]/input')
        time.sleep(1)
        self.dejaOpenTab = utilFunctions.switch_one_tab(self.driver, self.dejaOpenTab)
        self.wait_located_All_xpath('//*[@id="PeriodesPreCalculees"]/div[1]')
        print(dataFormulaire)
        if dataFormulaire['tva_type'] == 'ca3_mensuele':
            script = utilFunctions.script_include('a',dataFormulaire['mois']+' '+dataFormulaire['annee'])
            self.driver.execute_script(str(script), None)
            self.wait_located_All_xpath('//*[@id="contentFormulaire"]')
            utilFunctions.remplire_input_by_id(utilFunctions,self.driver,dataFormulaire['code'])
        elif dataFormulaire['tva_type'] == 'ca3_trimestre':
            textLien = 'er' if int(dataFormulaire['nbr_trimestre']) == 1 else 'ème'
            script = utilFunctions.script_include('a',dataFormulaire['nbr_trimestre']+textLien+' trimestre '+dataFormulaire['annee'])
            self.driver.execute_script(str(script), None)
            utilFunctions.remplire_input_by_id(utilFunctions,self.driver,dataFormulaire['code'])
        else:
            script = utilFunctions.script_include('a',dataFormulaire['annee'])
            self.driver.execute_script(str(script), None)
            utilFunctions.remplire_input_by_id(utilFunctions,self.driver,dataFormulaire['code'])
        return {'wawa':"wawa"}

    def repporter_credit_tva(self,data):
        #entrer dans declaration
        # utilFunctions.get_el_by_xpath(self.driver,'//*[@id="acces_par_impot"]/ul/li[1]/ul/li[1]/span/a').click()
        titreMenu = 'Déclarations'
        regex = '/voirDeclarationsTVA/g'
        script = utilFunctions.script_find_lien(titreMenu,regex)
        print(script)
        self.driver.execute_script(str(script), None)

        #choisir année dans declaration
        self.wait_located_All_xpath('//*[@id="raccourcis"]')
        print(data)
        print(type(data),'type data')
        script = utilFunctions.script_include('span','Année '+ str(data['annee']))
        self.driver.execute_script(str(script), None)

        #click contenue
        script = utilFunctions.script_include('a', data['mois'] +' '+str(data['annee']))
        self.driver.execute_script(str(script), None)

        #recuperer valeur sur tablaux
        self.wait_located_All_xpath('//*[@id="tva"]')
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        td_child = soup.find("td", attrs={'class':'caseNum1'}, text='27')
        print(type(td_child),'child type')
        tr_parent = td_child.find_parents('tr', limit=1)
        # all_td = tr_parent.findAll("td")
        value = {}
        for td in tr_parent:
            td_credit_tva = td.find("td", attrs={'class':'donneeMontant'})
            td_taxe_payer = td.find("td", attrs={'class':'donneeMontant txtEnValeurAlign2'})
            value = {
                'credit_tva': str(td_credit_tva.contents[0]) if str(td_credit_tva.contents[0]) != '\xa0\xa0' else '0' ,
                'taxe_a_payer': str(td_taxe_payer.contents[0]) if str(td_taxe_payer.contents[0]) != '\xa0\xa0' else '0',
            }
            print(value, 'valiny')
        return value

    def click_radio(self):
        time.sleep(1)
        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="membreIS_groupe_non"]')
        time.sleep(1)
        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="membreTVA_groupe_non"]')
        time.sleep(1)
        utilFunctions.click_element(utilFunctions, self.driver, '//*[@id="boutons"]/table[2]/tbody/tr/td[2]/span')

    def imprimer(self,siren):
        if self.driver != None :
            print('---------imprimer-------------------------')
            time.sleep(2)
            script = utilFunctions.script_include('a','impression')
            self.driver.execute_script(str(script), None)
            All_tab = utilFunctions.switch_one_tab(self.driver, self.dejaOpenTab)
            time.sleep(2)
            return self.check_table(siren)
        else:
            time.sleep(2)
            self.imprimer(siren)

    def check_table(self, siren):
        self.wait_located_All_xpath('/html/body/div[1]/table')
        element_table = utilFunctions.get_element_table(self.driver, BeautifulSoup, 'tableau','class')
        all_doc = element_table.findAll('tr')
        link = None
        for doc in all_doc:
            tag = doc.findAll('td')
            print('ATO 1----------------------------')
            for text in tag:
                content = text.contents
                print('ATO 2----------------------------')
                if siren in content[0] and self.compteurDown == 0:
                    img = doc.find('img')
                    print('ATO 3----------------------------')
                    print('---------compteur down = ', self.compteurDown)
                    if self.check_doc_ready(img['src']):
                        link = doc.find('a', href=True)
                        print('lien-----------------------------------------')
                        data = {
                                'url': 'https://cfspro.impots.gouv.fr/'+link['href'],
                                'cookieList' : self.get_coockies()
                            }
                        try:
                            pass
                            # self.driver.quit()
                            # time.sleep(5)
                            # s = self.set_session_cookie(data['cookieList'])
                            # self.download_file(s, data['url'])
                        except MaxRetryError:
                            pass
                        self.compteurDown = 1
                        self.dataDown = data
                        break
                    else:
                        #lencer recursive
                        print('RECURSIVE ------')
                        time.sleep(5)
                        self.check_table(siren)
                        break
        print('DATA TY -----------------------------------------')
        print(self.dataDown)
        return self.dataDown
        
                    
    
    def check_doc_ready(self,imgName):
        check = re.search('termine', imgName)
        if check is not None:
            return True
        else:
            return False

    def get_coockies(self):
        cookiesList = []
        i = 0
        for selenuim_coockies in self.driver.get_cookies():
            #cookie = requests.cookies.create_cookie(selenuim_coockies['name'], selenuim_coockies['value'])
            data = {
                'id':i,
                'name': selenuim_coockies['name'],
                'value': selenuim_coockies['value']
            }
            cookiesList.append(data)
            i += 1
        return cookiesList

    def set_session_cookie(self,listCookie):
        session = requests.Session()
        for cookie in listCookie:
            session.cookies.set_cookie(cookie)
        return session
    
    def download_file(self,session, urlDown):
        headers = {
            "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "Connection": "keep-alive"
        }
        with session.get(urlDown, stream=True, headers=headers) as r:
            with open('D:\\PROJET\\vao.pdf','wb') as f:
                for chunk in r.iter_content(4096):
                    if chunk:
                        f.write(chunk)
