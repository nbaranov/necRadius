from getpass import getpass
from time import sleep

from functions import readIPfromXLSX
from nec import nec

login = input("Введите логин: ")
password = getpass("Введите пароль: ")

listIP = readIPfromXLSX()

for ip in listIP:
    try:
        ne = nec(ip, login, password)
        ne.checkConfigRadius()
    except:
        sleep(1) #pause for close script
        continue

input("Для закрытия программы нажмите ENTER")
