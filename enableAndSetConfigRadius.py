#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
import sys

from ast import literal_eval
from functions import necAuth
from functions import checkStatus
from functions import readFileIP
from functions import logAndPrint
from getpass import getpass


    # turn on authentication over radius server
def turnOnRadius(user, sessionid, session, headers, url):    
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
def setParamRadius(lis, user, sessionid, session, headers, url):
    postData = {
        'CGI_ID': 'SET_LCT09RAD002_05', 
        'LIST': f'{lis}',
        'LIST_COUNT': 1,
        'USER_NAME': user,
        'SESSION_ID': sessionid
        }
    request = session.post(url, headers = headers, data = postData, timeout = 20)
    #print(request.text)
    return checkStatus(request)

# Start programm
# get ip adresess from file

def enableAndSetCongif(user, password, serverIndex, ipAddress, portNo, encryptionMethod, secretKey, pathIP, window):

    logAndPrint(f'''######################
    radius server param
    serverIndex = {serverIndex}               # line in parameters
    ipAddress = {ipAddress}      # IP adress radius server
    portNo = {portNo}                 # port number
    encryptionMethod = {encryptionMethod}          # 1 - User, 2 - CHAP
    secretKey = "{secretKey}"    # secret key
    ######################''', window, "", 0)

    listIP = readFileIP(pathIP)

    for ip in listIP:
        url = f'http://{ip}/cgi/lct.cgi'
        headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'LCT_POLLTIME=NONE',
        'Referer' : url
        }


        try:
            logAndPrint(f"Подключаюсь к элементу {ip}", window, "", 0)
            session, sessionid = necAuth(url, user, password, headers)
            logAndPrint(f'Подключение успешно', window)
            try:
                # check status radius server and turn on if its off
                postData = {'CGI_ID': 'GET_LCT09RAD001_01', 'USER_NAME': user, 'SESSION_ID': sessionid}
                request = session.post(url, headers = headers, data = postData, timeout = 20)
                dic = literal_eval(request.text)
                if (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "1":
                    if turnOnRadius(user, sessionid, session, headers, url) == True:
                        logAndPrint("Радиус сервер успешно включен", window)
                    else:
                        logAndPrint("Произошла ошибка при включении радиус сервера", window)
                elif (dic['data'][0]['authentication'][0]['radiusAuthMethod']) == "3":
                    logAndPrint("Радиус сервер был включен ранее", window)
                
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
                            if setParamRadius(newLis, user, sessionid, session, headers, url) == True:
                                logAndPrint("Удален старый радиус сервер", window)
                                logAndPrint(f'Параметры удаленного сервера: IP: {oldServ["ipAddress"]}, port: {oldServ["portNo"]}, encription: {"CHAP" if oldServ["encryptionMethod"] == "2" else "User"}, Secret Key: "{oldServ["secretKey"]}"', window)

                                lis = '[{'+f'"serverIndex":"{serverIndex}","ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]'
                                if setParamRadius(lis, user, sessionid, session, headers, url) == True:
                                    logAndPrint('Установлен новый радиус сервер', window)

                                    postData = {'CGI_ID': 'GET_LCT09RAD002_01', 'USER_NAME': user,'SESSION_ID': sessionid}
                                    request = session.post(url, headers = headers, data = postData, timeout = 20)
                                    dic = literal_eval(request.text)
                                    dic = dic['data'][0]['radiusRadiusServer'][0]
                                    logAndPrint(f'Параметры нового сервера: IP: {dic["ipAddress"]}, port: {dic["portNo"]}, encription: {"CHAP" if dic["encryptionMethod"] == "2" else "User"}, Secret Key: "{dic["secretKey"]}"', window)

                                else:
                                    logAndPrint("Произошла ошибка при установке параметров нового радиус сервера", window)
                            else:
                                logAndPrint(f"Произлшла ошибка при удалении настроек радиус сервера из слота: {serverIndex}", window)

                    except Exception:
                        logAndPrint(f'Нет настроеных радиус серверов', window)
                        lis = '[{'+f'"serverIndex": "{serverIndex}" ,"ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]' 
                        if setParamRadius(lis, user, sessionid, session, headers, url) == 0:
                                logAndPrint('Установлены настройки нового радиус сервера', window)
                        else:
                            logAndPrint(f"Произлшла ошибка при удалении настроек радиус сервера из слота: {serverIndex}", window)

                except Exception:
                    logAndPrint(f'Не удалось настроить параметры радиус сервера из слота: {serverIndex}', window)
                    logAndPrint(sys.exc_info()[1], window)
                    
            except Exception:
                logAndPrint('Не удалось включить радиус сервер', window)
                logAndPrint(sys.exc_info()[1], window)
                
        except Exception:
            logAndPrint('Не удалось авторизоваться на элементе', window)
            logAndPrint(sys.exc_info()[1], window)

