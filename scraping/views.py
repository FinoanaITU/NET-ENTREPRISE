from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from .netLog import NetLog
from selenium.common.exceptions import ElementNotInteractableException
import os

#driver prod
from .utils.prod.chrome import chrome

#driver local
#from .utils.local.chrome import chrome

app = Flask(__name__)
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config.from_object('config')

list_entreprise_gl = []
list_doc_gl = []
siren_gl = ''
driver = None


@app.route('/home')
def index():
    # initialise driver
    print(app.instance_path)
    filename = os.path.join(app.instance_path, 'templates')
    print(filename)

    global driver
    driver = chrome.driver()
    try:
        login = NetLog(driver).run_login(app.config['URL_PAGE'], app.config['USER_FIRST_NAME'],app.config['USER_LAST_NAME'], app.config['SIRET'], app.config['PASSWORD'])

    except ElementNotInteractableException as log_error:
        print('misy erreur')
        print(log_error)
        print(url_for('index'))

        return redirect(url_for('index'))

    list_services = []
    if login:
        list_services = NetLog(driver).list_services()
    return render_template('dashboard.html', listServices=list_services, services=True)


@app.route('/operation/<serviceName>')
def listeServices(serviceName):
    list_entreprise = NetLog(driver).list_entreprise(serviceName)
    if len(list_entreprise) != 0:
        global list_entreprise_gl
        list_entreprise_gl = list_entreprise
    return render_template('operation.html', listEntreprise=list_entreprise, listeDoc=0)


@app.route('/doc_urssaf/<siren>')
def docUrssaf(siren):
    list_doc = NetLog(driver).doc_urssaf(siren)
    if len(list_doc) != 0:
        global list_doc_gl
        global siren_gl
        siren_gl = siren
        list_doc_gl = list_doc
    return render_template('operation.html', listEntreprise=list_entreprise_gl, listeDoc=list_doc)


@app.route('/to_urrsaf/<periode>')
def toUrssaf(periode):
    log_urssaf = NetLog(driver).to_urssaf(periode, siren_gl)
    if log_urssaf:
        return render_template('operation.html', listEntreprise=list_entreprise_gl, listeDoc=list_doc_gl, urssaf_doc=periode)


@app.route('/download', methods=['GET', 'POST'])
def download():
    print(request.args)
    doc = request.args['document']
    type = request.args['types']
    print(doc)
    print(type)
    NetLog(driver).initialise_downloadFile(doc, type)
    return 'mandeha down'


@app.route('/logout')
def logout():
    driver.close()
    driver.quit()

    return 'déconnecter'
