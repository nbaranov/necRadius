import requests
import datetime

from ast import literal_eval
from bs4 import BeautifulSoup as bs

def necAuth(url, user, password, headers):
    # get session id first step authentication
    session = requests.session()
    post_data = {'CGI_ID': 'GET_LCT01000000_01', 'userName': user, 'password': password}
    auth = session.post(url, headers = headers, data = post_data, timeout = 50)
    soup = bs(auth.text, "lxml")
    sessionid = int(soup.find(id = "LCTSESSIONID").get('value'))

    # second step authentication 
    postData = {'CGI_ID': 'GET_LCT01000000_02', 'USER_NAME': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)

    # third step authentication posts
    postData = {'CGI_ID': 'GET_LCT01000000_03', 'userName': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)

    # fourth step authentication posts
    postData = {'CGI_ID': 'GET_LCT01000000_04', 'USER_NAME': user,'SESSION_ID': sessionid}
    session.post(url, headers = headers, data = postData, timeout = 50)

    # fifth step authentication posts
    postData = {'CGI_ID': 'GET_LCT01000000_05', 'userName': user,'SESSION_ID': sessionid}
    request = session.post(url, headers = headers, data = postData, timeout = 50)
    if checkStatus(request) == False:
        raise SystemError("Error authentication on nec RRL")

    # sixth step authentication posts
    postData = {'CGI_ID': 'GET_LCT99010100_01', 'loginuser': user, 'USER_NAME': user,'SESSION_ID': sessionid}
    request = session.post(url, headers = headers, data = postData, timeout = 50)
    if checkStatus(request) == False:
        raise SystemError("Error authentication on nec RRL")

    return session, sessionid


def checkStatus(request):
    if int(literal_eval(request.text)['status'][0]['cgi_status']) == 0:
        return True
    return False


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


def logAndPrint(massage, ind="\t\t   ", dateform=-8):
    date = timenow()[dateform:]
    print(f"{ind}{massage}")
    with open('logs.log', 'a', encoding="UTF-8") as logs:
        logs.write(f'{ind}{date} {massage}\n')