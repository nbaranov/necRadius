import time
import requests

from bs4 import BeautifulSoup as bs

######################
user = "Admin"
password = "12345678"
ip = '10.174.108.75'
######################

url = f"http://{ip}/"
refer = f'http://{ip}/cgi/lct.cgi'

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'LCT_POLLTIME=NONE',
    'Referer' : url
}

login_data = {
    'CGI_ID': 'GET_LCT01000000_01',
    'userName': user,
    'password': password
}


session = requests.session()
auth = session.post(refer, headers=headers, data=login_data, timeout=20)
soup = bs(auth.text, "lxml")
sessionid = int(soup.find(id="LCTSESSIONID").get('value'))

print(f"Элемент {ip} сессия {sessionid}")

def postData(cgi, lis):
    data = {
        'CGI_ID': cgi,
        'LIST': lis,
        'LIST_COUNT': 1,
        'USER_NAME': user,
        'SESSION_ID': sessionid
    }

    return data

# open user authentication
radius = session.post(refer, headers=headers, data=postData('GET_LCT09RAD001_01', None), timeout=20)
print(radius.text)

# post open settings
radius = session.post(refer, headers=headers, data=postData('GET_LCT09RAD001_02', [{"index":"1"}]), timeout=20)
print(radius.text)

#change settings
radius = session.post(refer, headers=headers, data=postData('SET_LCT09RAD001_05', [{"index":"1","radiusAuthMethod":"3","radiusAuthSequence":"2"}]), timeout=20)
print(radius.text)