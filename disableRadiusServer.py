#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
import sys

from ast import literal_eval
from functions import necAuth
from functions import checkStatus
from functions import timenow
from functions import readFileIP
from functions import logAndPrint
from getpass import getpass


# turn on authentication over radius server
def turnOffRadius():    
    postData = {
        'CGI_ID': 'SET_LCT09RAD001_05', 
        'LIST': '[{"index":"1","radiusAuthMethod":"1","radiusAuthSequence":"2"}]', 
        'LIST_COUNT': 1, 
        'USER_NAME': user,
        'SESSION_ID': sessionid
    }
    request = session.post(url, headers = headers, data = postData, timeout = 20)
    return checkStatus(request)

# Start programm
# get ip adresess from file

user = input("Введите логин: ")
password = getpass("Введите пароль: ")

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
        try:
            # check status radius server and turn on if its off
            postData = {'CGI_ID': 'GET_LCT09RAD001_01', 'USER_NAME': user, 'SESSION_ID': sessionid}
            request = session.post(url, headers = headers, data = postData, timeout = 20)
            dic = literal_eval(request.text)
            if (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "3":
                if turnOffRadius() == True:
                    logAndPrint("Радиус сервер успешно выключен")
                else:
                    logAndPrint("Произошла ошибка при выключении радиус сервера")
            elif (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "1":
                logAndPrint("Радиус сервер был выключен ранее")
            
        except Exception:
            logAndPrint('Не удалось выключить радиус сервер')
            logAndPrint(sys.exc_info()[1])
            
    except Exception:
        logAndPrint('Не удалось авторизоваться на элементе')
        logAndPrint(sys.exc_info()[1])

input("Для закрытия программы нажмите ENTER")