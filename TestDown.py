import requests

data = requests.get('http://127.0.0.1:5000/login_impot/334138591')
dataJson = data.json()


def create_cookie_list(dataJson):
    cookieList = []
    for c in dataJson:
        cookie = requests.cookies.create_cookie(c['name'], c['value'])
        cookieList.append(cookie)
    return cookieList

def set_session_cookie(listCookie):
        session = requests.Session()
        for cookie in listCookie:
            session.cookies.set_cookie(cookie)
        return session
    
def download_file(session, urlDown):
    print('Debut Down')
    headers = {
        "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Connection": "keep-alive"
    }
    with session.get(urlDown, stream=True, headers=headers) as r:
        with open('D:\\PROJET\\334138591.pdf','wb') as f:
            for chunk in r.iter_content(4096):
                if chunk:
                    f.write(chunk)
    
    print('DOWN OK')


cookieList = create_cookie_list(dataJson['cookieList'])
session = set_session_cookie(cookieList)
download_file(session, dataJson['url'])