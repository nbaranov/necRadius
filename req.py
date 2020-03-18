import datetime
import requests
import sys
import time

from bs4 import BeautifulSoup as bs
from ast import literal_eval

######################
user = "Admin"
password = "12345678"

#radius server param
serverIndex = "1"               # line in parameters
ipAddress = "10.190.10.36"      # IP adress radius server
portNo = "1812"                 # port number
encryptionMethod = "2"          # 1 - User, 2 - CHAP
secretKey = "nec_rrl_center"    # secret key
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


    # turn on authentication over radius server
def turnOnRadius():    
    postData = {
        'CGI_ID': 'SET_LCT09RAD001_05', 
        'LIST': '[{"index":"1","radiusAuthMethod":"3","radiusAuthSequence":"2"}]', 
        'LIST_COUNT': 1, 
        'USER_NAME': user,
        'SESSION_ID': sessionid
    }
    request = session.post(url, headers = headers, data = postData, timeout = 20)
    return checkStatus(request)

# set parametrs of radius server
def setParamRadius(lis):
    postData = {
        'CGI_ID': 'SET_LCT09RAD002_05', 
        'LIST': f'{lis}',
        'LIST_COUNT': 1,
        'USER_NAME': user,
        'SESSION_ID': sessionid
        }
    request = session.post(url, headers = headers, data = postData, timeout = 20)
    return checkStatus(request)


def logAndPrint(massage, ind="\t\t   ", dateform=-8):
    date = timenow()[dateform:]
    print(f"{ind}{massage}")
    with open('logs.log', 'a', encoding="UTF-8") as logs:
        logs.write(f'{ind}{date} {massage}\n')

def checkStatus(reqiest):
    return int(literal_eval(request.text)['status'][0]['cgi_status'])

# Start programm
# get ip adresess from file

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
        try:
            # check status radius server and turn on if its off
            postData = {'CGI_ID': 'GET_LCT09RAD001_01', 'USER_NAME': user, 'SESSION_ID': sessionid}
            request = session.post(url, headers = headers, data = postData, timeout = 20)
            dic = literal_eval(request.text)
            if (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "1":
                if turnOnRadius() == 0:
                    logAndPrint("Радиус сервер успешно включен")
                else:
                    logAndPrint("Произошла ошибка при включении радиус сервера")
            elif (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "3":
                logAndPrint("Радиус сервер был включен ранее")
            
            # check settings of radius seerver, delete string if fun and set new 
            try:
                postData = {'CGI_ID': 'GET_LCT09RAD002_01', 'USER_NAME': user,'SESSION_ID': sessionid}
                request = session.post(url, headers = headers, data = postData, timeout = 20)
                dic = literal_eval(request.text)
                try:
                    if (dic['data'][0]['radiusRadiusServer'][0]['serverIndex']) == serverIndex:
                        oldServ = dic['data'][0]['radiusRadiusServer'][0]
                        oldServ.update({'rowStatus': '6'}) 
                        lis = str([oldServ])
                        newLis = str()
                        for i in lis:
                            if i == "'":
                                newLis = newLis + '"'
                            elif i == " ":
                                continue
                            else:
                                newLis = newLis + i 
                        if setParamRadius(newLis) == 0:
                            logAndPrint("Удален старый радиус сервер")
                            logAndPrint(f'Параметры удаленного сервеера: IP: {oldServ["ipAddress"]}, port: {oldServ["portNo"]}, encription: {"CHAP" if oldServ["encryptionMethod"] == "2" else "User"}, Secret Key: "{oldServ["secretKey"]}"')

                            lis = '[{'+f'"serverIndex":"{serverIndex}","ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]'
                            if setParamRadius(lis) == 0:
                                logAndPrint('Установлен новый радиус сервер')
                            else:
                                logAndPrint("Произошла ошибка при установке параметров нового радиус сервера")
                        else:
                            logAndPrint("Произлшла ошибка при удалении радиус сервера")

                except Exception:
                    logAndPrint(f'Нет настроеных радиус серверов')
                    lis = '[{'+f'"serverIndex": "{serverIndex}" ,"ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]' 
                    if setParamRadius(lis) == 0:
                            logAndPrint('Установлен новый радиус сервер')
                    else:
                        logAndPrint("Произошла ошибка при установке параметров нового радиус сервера")

            except Exception:
                logAndPrint('Не удалось настроить параметры радиус сервера')
                logAndPrint(sys.exc_info()[1])
                
        except Exception:
            logAndPrint('Не удалось включить радиус сервер')
            logAndPrint(sys.exc_info()[1])
            
    except Exception:
        logAndPrint('Не удалось авторизоваться на элементе')
        logAndPrint(sys.exc_info()[1])

input("Для закрытия программы нажмите ENTER")