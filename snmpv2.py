####################################
INDEX = '1'             #строка для застроек
COMNAME = "central"     #имя коммьюнити
ACCLEVEL = "3"          #уровнеть доступна 1-operator 2-config 3-admin
ACCCONTROL = "0"        #контроль доступна 0-выкл, 1 -вкл
ACCADRESS = "0.0.0.0"   #адресс доступа, если контроль выключен поставить 0.0.0.0 
SUBNETMASK = "0"        #маска доступа, если контроль выключен поставить 0
####################################

from getpass import getpass
from time import sleep

from functions import readIPfromXLSX
from functions import logAndPrint
from nec import nec

login =  input("Введите логин: ")
password = getpass("Введите пароль: ")

listIP = readIPfromXLSX()
for i in range(len(listIP)):
    print(f'Узел {i+1} из {len(listIP)}')
    try:
        ne = nec(listIP[i], login, password)
        snmp = ne.getSNMPset()
        if snmp["snmp"][0]['snmpv1v2c'] != '2':
            ne.turnOnSNMP(snmp["snmp"][0])
        else: logAndPrint("SNMPv2 уже был включен")

        ne.setSNMPcom(INDEX, COMNAME, ACCLEVEL, ACCCONTROL, ACCADRESS, SUBNETMASK)
    except:
        sleep(1) # пауза для прерывания
        continue

