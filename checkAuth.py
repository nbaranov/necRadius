import datetime
import requests
import sys
import time

from ast import literal_eval
from bs4 import BeautifulSoup as bs
from getpass import getpass


######################
user = input("Введите лоигин: ")
password = getpass("Введите пароль: ")
######################

session = None
sessionid = None

def timenow():
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

def readFileIP(path):
    ipList = []
    with open(path, 'r', encoding='utf_16_le') as inFile:
        for line in inFile:
            line = line.strip(" \n")
            if line[0] == ";":
                ipList.append(line.split(";")[1])
    return ipList

def authentication(url):
    # get session id first step authentication
    session = requests.session()
    post_data = {'CGI_ID': 'GET_LCT01000000_01', 'userName': user, 'password': password}
    auth = session.post(url, headers = headers, data = post_data, timeout = 50)
    soup = bs(auth.text, "lxml")
    sessionid = int(soup.find(id = "LCTSESSIONID").get('value'))

    # second step authentication 
    postData = {'CGI_ID': 'GET_LCT01000000_02', 'USER_NAME': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # third step authentication posts
    postData = {'CGI_ID': 'GET_LCT01000000_03', 'userName': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # fourth step authentication posts
    postData = {'CGI_ID': 'GET_LCT01000000_04', 'USER_NAME': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # fifth step authentication posts
    postData = {'CGI_ID': 'GET_LCT01000000_05', 'userName': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # sixth step authentication posts
    postData = {'CGI_ID': 'GET_LCT99010100_01', 'loginuser': 'Admin', 'USER_NAME': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)
    #print(request.text) # status and information

    return session, sessionid

def logAndPrint(massage, ind="\t\t   ", dateform=-8):
    date = timenow()[dateform:]
    print(f"{ind}{massage}")
    with open('logs.log', 'a', encoding="UTF-8") as logs:
        logs.write(f'{ind}{date} {massage}\n')

listIP = readFileIP('RRL_list.csv')

for ip in listIP:
    url = f'http://{ip}/cgi/lct.cgi'
    headers = {
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'LCT_POLLTIME=NONE',
    'Referer' : url
    }


    try:
        logAndPrint(f"Подключаюсь к элементу {ip}", "", 0)
        session, sessionid = authentication(url)
        logAndPrint(f'Подключение успешно')

    except Exception:
        logAndPrint('Не удалось авторизоваться на элементе')
        logAndPrint(sys.exc_info()[1])

input("Для закрытия программы нажмите ENTER")