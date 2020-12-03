import os

URL_PAGE = "https://www.net-entreprises.fr/"

#for Net-entreprise
SIRET = '75077863100010'
USER_FIRST_NAME = 'dabou'
USER_LAST_NAME = 'stephane'
PASSWORD = 'Sda.std92'

BASE_URL = 'http://127.0.0.1:5000/'

PATH_FILE = 'D:\\Perso'

#for Impot
URL_IMPOT = 'https://cfspro.impots.gouv.fr/LoginAccess'
EMAIL_IMPOT= 'fiscal@sdaexpertise.fr'
PASSWORD_IMPOT= 'Sda.std92'

#AWS S3 CONFIG
S3_BUCKET                 = 'sda-scraping-backup'
S3_KEY                    = 'AKIASY7R2CEMSQVEP3ZP'
S3_SECRET                 = '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'
S3_LOCATION               = 'https://191096295705.signin.aws.amazon.com/console'

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000


