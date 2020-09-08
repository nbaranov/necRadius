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
from time import sleep

from functions import readIPfromXLSX
from functions import logAndPrint
from nec import nec


# Start programm

login = input("Введите логин: ")
password = getpass("Введите пароль: ")
setdic = {
    "serverIndex":SERVERINDEX,
    "ipAddress":IPSERVER,
    "portNo":PORT,
    "encryptionMethod":ENCRYPTIONMETHOD,
    "secretKey":SECRETKEY
}

logAndPrint(f'''######################
radius server param
serverIndex = {SERVERINDEX}               # line in parameters
ipAddress = {IPSERVER}      # IP adress radius server
portNo = {PORT}                 # port number
encryptionMethod = {ENCRYPTIONMETHOD}          # 1 - User, 2 - CHAP
secretKey = "{SECRETKEY}"    # secret key
######################''', "", 0)


listIP = readIPfromXLSX("NEnec.xlsx")

for ip in listIP:
    try:
        ne = nec(ip, login, password)
        try:
            if not ne.checkStatusRadius():
                ne.turnOnRadius()
            else:
                logAndPrint("Радиус сервер был включен ранее")
            
            # check settings of radius seerver, delete string if find and set new 
            try:
                setings = ne.getRadiusSet()
                for set in setings:
                    del set['rowStatus']
                if setings[int(SERVERINDEX) - 1]['serverIndex'] == SERVERINDEX:
                    try:
                        if setings[int(SERVERINDEX) - 1] == setdic:    
                            logAndPrint("Радиус уже настроен заданными параметрами")
                        elif (setings[int(SERVERINDEX) - 1]['serverIndex']) == SERVERINDEX:
                            oldServ = setings[int(SERVERINDEX) - 1]
                            if ne.delParamRadius(oldServ) == True:
                                logAndPrint("Удален старый радиус сервер")
                                logAndPrint(f'Параметры удаленного сервера: IP: {oldServ["ipAddress"]}, port: {oldServ["portNo"]}, encription: {"CHAP" if oldServ["encryptionMethod"] == "2" else "User"}, Secret Key: "{oldServ["secretKey"]}"')

                                if ne.setParamRadius(setdic) == True:
                                    logAndPrint('Установлен новый радиус сервер')
                                    setings = ne.getRadiusSet()
                                    setings = setings[int(SERVERINDEX) - 1]
                                    logAndPrint(f'Параметры нового сервера: IP: {setings["ipAddress"]}, port: {setings["portNo"]}, encription: {"CHAP" if setings["encryptionMethod"] == "2" else "User"}, Secret Key: "{setings["secretKey"]}"')
                                else:
                                    logAndPrint("Произошла ошибка при установке параметров нового радиус сервера")
                            else:
                                logAndPrint(f"Произлшла ошибка при удалении настроек радиус сервера из слота: {SERVERINDEX}")
                    
                    except Exception:
                        logAndPrint(f'Не удалось настроить параметры радиус сервера из слота: {SERVERINDEX}')
                        logAndPrint(sys.exc_info()[1])

            except Exception:
                logAndPrint(f'Нет настроеных радиус серверов')
                if ne.setParamRadius(setdic) == True:
                        logAndPrint('Установлены настройки нового радиус сервера')
                else:
                    logAndPrint(f'Не удалось настроить параметры радиус сервера из слота: {SERVERINDEX}')
                
        except Exception:
            logAndPrint('Не удалось включить радиус сервер')
            logAndPrint(sys.exc_info()[1])
            
    except Exception:
        logAndPrint('Не удалось авторизоваться на элементе')
        sleep(1) # пауза для прерывания
        continue
        

input("Для закрытия программы нажмите ENTER")
