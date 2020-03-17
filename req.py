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
serverIndex = "1"               # line in param 
ipAddress = "10.190.10.36"      # IP server
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

def authentication(full_url):
    # get session id first step authentication
    session = requests.session()
    post_data = {'CGI_ID': 'GET_LCT01000000_01', 'userName': user, 'password': password}
    auth = session.post(full_url, headers = headers, data = post_data, timeout = 50)
    soup = bs(auth.text, "lxml")
    sessionid = int(soup.find(id = "LCTSESSIONID").get('value'))

    # second step authentication 
    postData = {'CGI_ID': f'GET_LCT01000000_02', 'USER_NAME': user,'SESSION_ID': sessionid}
    request = session.post(full_url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # third step authentication posts
    postData = {'CGI_ID': f'GET_LCT01000000_03', 'userName': user,'SESSION_ID': sessionid}
    request = session.post(full_url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # fourth step authentication posts
    postData = {'CGI_ID': f'GET_LCT01000000_04', 'USER_NAME': user,'SESSION_ID': sessionid}
    request = session.post(full_url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # fifth step authentication posts
    postData = {'CGI_ID': f'GET_LCT01000000_05', 'userName': user,'SESSION_ID': sessionid}
    request = session.post(full_url, headers = headers, data = postData, timeout = 50)
    #print(request.text) #status

    # sixth step authentication posts
    postData = {'CGI_ID': f'GET_LCT99010100_01', 'loginuser': 'Admin', 'USER_NAME': user,'SESSION_ID': sessionid}
    request = session.post(full_url, headers = headers, data = postData, timeout = 50)
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
    request = session.post(full_url, headers = headers, data = postData, timeout = 20)
    #print(radius.text)

# set parametrs of radius server
def setParamRadius(lis):
    postData = {
        'CGI_ID': 'SET_LCT09RAD002_05', 
        'LIST': lis,
        'LIST_COUNT': "1",
        'USER_NAME': user,
        'SESSION_ID': sessionid
        }
    print(lis)
    request = session.post(full_url, headers = headers, data = postData, timeout = 20)
    print(request.text)


# Start programm
# get ip adresess from file

listIP = readFileIP('RRL_list.csv')

for ip in listIP:
    short_url = f'http://{ip}/'
    full_url = f'http://{ip}/cgi/lct.cgi'
    headers = {
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'LCT_POLLTIME=NONE',
    'Referer' : short_url
    }


    try:
        print(f"connect to {ip}")
        with open('logs.log', 'a', encoding="UTF-8") as logs:
            logs.write(f'{timenow()} Подключаюсь к элемунту {ip}\n')
        session, sessionid = authentication(full_url)
        print (f'\t authentication sucsess')
        try:
            # check status radius server and turn on if its off
            postData = {'CGI_ID': 'GET_LCT09RAD001_01', 'USER_NAME': user, 'SESSION_ID': sessionid}
            request = session.post(full_url, headers = headers, data = postData, timeout = 20)
            dic = literal_eval(request.text)
            if (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "1":
                turnOnRadius()
                with open('logs.log', 'a', encoding="UTF-8") as logs:
                    logs.write(f'\t\t{timenow()} Радиус сервер успешно включен на элементе: {ip}\n')

            elif (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "3":
                with open('logs.log', 'a', encoding="UTF-8") as logs:
                    logs.write(f'\t\t{timenow()} На элементе: {ip} радиус сервер был включен ранее\n')
            
            # check settings of radius seerver, delete string if fun and set new 
            try:
                postData = {'CGI_ID': f'GET_LCT09RAD002_01', 'USER_NAME': user,'SESSION_ID': sessionid}
                request = session.post(full_url, headers = headers, data = postData, timeout = 20)
                dic = literal_eval(request.text)
                try:
                    if (dic['data'][0]['radiusRadiusServer'][0]['serverIndex']) == "1":
                        lis = dic['data'][0]['radiusRadiusServer'][0]
                        lis.update({'rowStatus': '6'}) 
                        lis = str([lis])
                        newLis = str()
                        for i in lis:
                            if i == "'":
                                newLis = newLis + '"'
                            elif i == " ":
                                continue
                            else:
                                newLis = newLis + i 

                        postData = {'CGI_ID': 'GET_LCT09RAD002_01', 'USER_NAME': user, 'SESSION_ID': sessionid}
                        request = session.post(full_url, headers = headers, data = postData, timeout = 20)

                        postData = {'CGI_ID': 'GET_LCT09RAD002_03', "LIST": f"[{dic['data'][0]['radiusRadiusServer'][0]['serverIndex']}]", 'USER_NAME': user, 'SESSION_ID': sessionid}
                        request = session.post(full_url, headers = headers, data = postData, timeout = 20)

                        setParamRadius(f'"{newLis}"')
                        
                        print(f"\t Удален старый радиус  сервевр на элементе: {ip}")
                        with open('logs.log', 'a', encoding="UTF-8") as logs:
                            logs.write(f'\t\t{timenow()} Удален старый радиус серве {ip}\n \t\t Параметры удаленного сервеера {lis}\n')

                        lis = '[{'+f'"serverIndex": "{serverIndex}" ,"ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]' 
                        setParamRadius(f'"{lis}"')
                        print(f"\tУстановлен новый радиус сервевр на элементе: {ip}")
                        with open('logs.log', 'a', encoding="UTF-8") as logs:
                            logs.write(f'\t\t{timenow()} Установлен новый радиус серве {ip}\n')
                except Exception:
                    print(f'\t нет настроеных радиус серверов')
                    lis = '[{'+f'"serverIndex": "{serverIndex}" ,"ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]' 
                    setParamRadius(lis)
                    print(f"\t Установлен новый радиус сервевр на элементе: {ip}")
                    with open('logs.log', 'a', encoding="UTF-8") as logs:
                        logs.write(f'\t\t{timenow()} Установлен новый радиус сервер на элементе: {ip}\n')
                
            except Exception:
                print(f'\t Не удалось настроить параметры радиус сервера')
                print(sys.exc_info()[1])
                with open('logs.log', 'a', encoding="UTF-8") as logs:
                    logs.write(f'\t\t{timenow()} Не удалось настроить параметры радиус сервера на элементе: {ip}\n')

        except Exception:
            print(f'\t Не удалось включить радиус сервер')
            print(sys.exc_info()[1])
            with open('logs.log', 'a', encoding="UTF-8") as logs:
                logs.write(f'\t\t{timenow()} Не удалось включить радиус сервер на элементе: {ip}\n')
      
    except Exception:
        print(f'\t Не удалось авторизоваться на элементе')
        print(sys.exc_info()[1])
        with open('logs.log', 'a', encoding="UTF-8") as logs:
            logs.write(f'\t\t{timenow()}Не удалось авторизоваться на элементе: {ip}\n')