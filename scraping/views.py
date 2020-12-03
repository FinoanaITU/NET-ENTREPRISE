from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from .netLog import NetLog
from selenium.common.exceptions import ElementNotInteractableException
from .Impot import Impot
from .utils.aws import S3Connect
import os

# driver prod
from .utils.prod.chrome import chrome

# driver local
#from .utils.local.chrome import chrome

app = Flask(__name__)
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config.from_object('config')

list_entreprise_gl = []
list_doc_gl = []
siren_gl = ''
driver_gl = None
newChoice_gl = False
rs_sociale_gl = ''
period_gl = None
siren_choice_gl = None
list_services_gl = []
serviceName_gl = None

#for NET-ENTREPRISE
@app.route('/home')
def index():
    # initialise driver
    global driver_gl
    global list_services_gl
    list_services = []
    if driver_gl == None:
        basedir = os.path.abspath(os.path.dirname(__file__))
        driver_gl = chrome(basedir).driver()
        try:
            login = NetLog(driver_gl).run_login(app.config['URL_PAGE'], app.config['USER_FIRST_NAME'],app.config['USER_LAST_NAME'], app.config['SIRET'], app.config['PASSWORD'])

        except ElementNotInteractableException as log_error:
            print('misy erreur')
            print(log_error)
            print(url_for('index'))

            return redirect(url_for('index'))
        if login:
            list_services = NetLog(driver_gl).list_services()
            list_services_gl = list_services
    elif driver_gl != None and len(list_services_gl) != 0 :
        list_services = list_services_gl
        driver_gl.get('https://portail.net-entreprises.fr/priv/declarations')

    return render_template('dashboard.html', listServices=list_services, services=True)


@app.route('/operation/<serviceName>')
def listeServices(serviceName):
    global serviceName_gl
    if serviceName_gl == None:
        serviceName_gl =  serviceName
        list_entreprise = NetLog(driver_gl).list_entreprise(serviceName)
        if len(list_entreprise) != 0:
            global list_entreprise_gl
            list_entreprise_gl = list_entreprise
    else:
        list_entreprise = list_entreprise_gl
        driver_gl.get('https://ducs.net-entreprises.fr/com.netducsi.client.htmlhome/servlets/AccrochageEFIEDIChoiceOut.do')
        
    return render_template('operation.html', listEntreprise=list_entreprise, listeDoc=0, serviceName = serviceName_gl)


@app.route('/doc_urssaf')
def docUrssaf():
    rs_sociale = request.args.get('rscociale', None)
    noDoc = False
    global newChoice_gl
    global rs_sociale_gl
    global siren_choice_gl
    siren = request.args.get('siren', None)
    rs_sociale_gl = rs_sociale
    siren_choice_gl =  request.args.get('sirenChoice', None)
    print('siren_choice_gl------------------------')
    print(siren_choice_gl)
    list_doc = NetLog(driver_gl).doc_urssaf(siren, newChoice_gl, siren_choice_gl)
    # check new siren choice
    for list in list_doc:
        if 'newChoice' in list:
            newChoice_gl = True
        else:
            newChoice_gl = False
    if len(list_doc) != 0:
        global list_doc_gl
        global siren_gl
        siren_gl = siren
        existDoc = 'noDoc' in list_doc[0]
        if existDoc == False:
            list_doc_gl = list_doc
            noDoc = existDoc
        else:
            noDoc = existDoc
    return render_template('operation.html', listEntreprise=list_entreprise_gl, listeDoc=list_doc, noDoc=noDoc, newChoice=newChoice_gl, rs_sociale=rs_sociale_gl, siren_choice_gl=siren_choice_gl, last_siren=siren, serviceName = serviceName_gl)


@app.route('/to_urrsaf')
def toUrssaf():
    periode = request.args.get('periode', None)
    siren_choice =  request.args.get('lastSiren', None)
    print('newChoice_gl------------------------')
    print(newChoice_gl)
    if newChoice_gl:
        siren = siren_choice_gl
    else:
        siren = siren_gl
    log_urssaf = NetLog(driver_gl).to_urssaf(periode, siren, siren_choice)
    if log_urssaf:
        return render_template('download.html', urssaf_doc=periode, rs_sociale=rs_sociale_gl, serviceName = serviceName_gl)


@app.route('/download', methods=['GET', 'POST'])
def download():
    print(request.args)
    doc = request.args['document']
    type = request.args['types']
    print(doc)
    print(type)
    NetLog(driver_gl).initialise_downloadFile(doc, type)
    driver_gl.get('https://ducs.net-entreprises.fr/com.netducsi.client.htmlhome/servlets/AccrochageEFIEDIChoiceOut.do')
    return render_template('operation.html', listEntreprise=list_entreprise_gl, listeDoc=0, serviceName = serviceName_gl, download = True)


@app.route('/logout')
def logout():
    driver_gl.quit()
    return 'déconnecter'


@app.route('/retour_choix_entreprise')
def to_choix():
    NetLog(driver_gl).to_choix()
    return render_template('operation.html', listEntreprise=list_entreprise_gl, serviceName = serviceName_gl)

#FOR IMPOT
@app.route('/login_impot')
def login_impot():
    global driver_gl
    login_check = False
    if driver_gl == None:
        basedir = S3Connect.sign_s3('test','pdf')
        print('URL ------------------------------------------')
        print(basedir)
        # basedir = os.path.abspath(os.path.dirname(__file__))
        driver_gl = chrome(basedir['url']).driver()
        impot = Impot(driver_gl)
        login_check = impot.connnect(app.config['URL_IMPOT'], app.config['EMAIL_IMPOT'], app.config['PASSWORD_IMPOT'])
        if login_check:
            impot.choix_dossier([3,3,4])
            to_fiscale = impot.compte_fiscale()
            if to_fiscale:
                impot.imprimer(334138591)
    return str(login_check)