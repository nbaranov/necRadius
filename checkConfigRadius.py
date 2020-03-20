import datetime
import requests
import sys

from ast import literal_eval
from bs4 import BeautifulSoup as bs
from getpass import getpass

from functions import necAuth
from functions import readFileIP
from functions import logAndPrint

user = input("Введите логин: ")
password = getpass("Введите пароль: ")
session = None
sessionid = None

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
        session, sessionid = necAuth(url, user, password, headers)
        logAndPrint(f'Подключение успешно')

        postData = {'CGI_ID': 'GET_LCT09RAD002_01', 'USER_NAME': user,'SESSION_ID': sessionid}
        request = session.post(url, headers = headers, data = postData, timeout = 20)
        dic = literal_eval(request.text)
        dic = dic['data'][0]['radiusRadiusServer'][0]
        logAndPrint(f'Параметры радиус сервера сервера: IP: {dic["ipAddress"]}, port: {dic["portNo"]}, encription: {"CHAP" if dic["encryptionMethod"] == "2" else "User"}, Secret Key: "{dic["secretKey"]}"')

    except Exception:
        logAndPrint('Не удалось авторизоваться на элементе')
        logAndPrint(sys.exc_info()[1])

input("Для закрытия программы нажмите ENTER")