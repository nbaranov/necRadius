######################
#radius server param
SERVERINDEX = "1"               # line in parameters
IPSERVER = "10.190.10.36"       # IP adress radius server
PORT = "1812"                   # port number
ENCRYPTIONMETHOD = "1"          # 1 - User, 2 - CHAP
SECRETKEY = "nec_rrl_center"    # secret key
######################

import requests
import sys

from getpass import getpass

from functions import readIPfromXLSX
from functions import logAndPrint
from nec import nec


# Start programm

login = input("Введите логин: ")
password = getpass("Введите пароль: ")
setdic = {
    "serverIndex":"{SERVERINDEX}",
    "ipAddress":"{IPSERVER}",
    "portNo":"{PORT}",
    "encryptionMethod":"{ENCRYPTIONMETHOD}",
    "secretKey":"{SECRETKEY}"
}

logAndPrint(f'''######################
radius server param
serverIndex = {SERVERINDEX}               # line in parameters
ipAddress = {IPSERVER}      # IP adress radius server
portNo = {PORT}                 # port number
encryptionMethod = {ENCRYPTIONMETHOD}          # 1 - User, 2 - CHAP
secretKey = "{SECRETKEY}"    # secret key
######################''', "", 0)


listIP = readIPfromXLSX

for ip in listIP:
    try:
        nec = nec(ip, login, password)
        try:
            if nec.checkStatusRadius():
                nec.turnOnRadius()
            else:
                logAndPrint("Радиус сервер был включен ранее")
            
            # check settings of radius seerver, delete string if find and set new 
            try:
                setings = nec.getRadiusSet()
                for set in setings:
                    del set['rowStatus']
                if setings[SERVERINDEX - 1]['serverIndex'] == SERVERINDEX:
                    if setings[SERVERINDEX - 1] == setdic:
                        logAndPrint("Радиус уже настроен заданными параметрами")


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
                        if setParamRadius(newLis) == True:
                            logAndPrint("Удален старый радиус сервер")
                            logAndPrint(f'Параметры удаленного сервера: IP: {oldServ["ipAddress"]}, port: {oldServ["portNo"]}, encription: {"CHAP" if oldServ["encryptionMethod"] == "2" else "User"}, Secret Key: "{oldServ["secretKey"]}"')

                            lis = '[{'+f'"serverIndex":"{serverIndex}","ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]'
                            if setParamRadius(lis) == True:
                                logAndPrint('Установлен новый радиус сервер')

                                postData = {'CGI_ID': 'GET_LCT09RAD002_01', 'USER_NAME': user,'SESSION_ID': sessionid}
                                request = session.post(url, headers = headers, data = postData, timeout = 20)
                                dic = literal_eval(request.text)
                                dic = dic['data'][0]['radiusRadiusServer'][0]
                                logAndPrint(f'Параметры нового сервера: IP: {dic["ipAddress"]}, port: {dic["portNo"]}, encription: {"CHAP" if dic["encryptionMethod"] == "2" else "User"}, Secret Key: "{dic["secretKey"]}"')

                            else:
                                logAndPrint("Произошла ошибка при установке параметров нового радиус сервера")
                        else:
                            logAndPrint(f"Произлшла ошибка при удалении настроек радиус сервера из слота: {serverIndex}")

                except Exception:
                    logAndPrint(f'Нет настроеных радиус серверов')
                    lis = '[{'+f'"serverIndex": "{serverIndex}" ,"ipAddress":"{ipAddress}","portNo":"{portNo}","encryptionMethod":"{encryptionMethod}","secretKey":"{secretKey}","rowStatus":"4"'+'}]' 
                    if setParamRadius(lis) == 0:
                            logAndPrint('Установлены настройки нового радиус сервера')
                    else:
                        logAndPrint(f"Произлшла ошибка при удалении настроек радиус сервера из слота: {serverIndex}")

            except Exception:
                logAndPrint(f'Не удалось настроить параметры радиус сервера из слота: {serverIndex}')
                logAndPrint(sys.exc_info()[1])
                
        except Exception:
            logAndPrint('Не удалось включить радиус сервер')
            logAndPrint(sys.exc_info()[1])
            
    except Exception:
        logAndPrint('Не удалось авторизоваться на элементе')
        logAndPrint(sys.exc_info()[1])

input("Для закрытия программы нажмите ENTER")