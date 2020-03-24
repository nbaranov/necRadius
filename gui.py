import PySimpleGUI as sg
import subprocess
import sys
from multiprocessing import Process
from enableAndSetConfigRadius import enableAndSetCongif
from checkConfigRadius import checkConfig


def readConfig():
    with open(".lastconfig", "r", encoding="UTF-8") as ls:
        lis = ls.readlines()
        ls = []
        for i in range(0,9):
            ls.append(lis[i].strip())
        return ls

def writeConfig(values):
    with open(".lastconfig", "w", encoding="UTF-8") as ls:
        for i in range(len(values)-1):
            ls.write(f"{values[i]}\n")

def start(func, args):
    p = Process(target=func, args=args)
    p.start()

try:
    ls = readConfig()
    user = ls[0]
    password = ls[1]
    serverIndex = ls[2]
    ipAddress = ls[3]
    portNo = ls[4]
    encryptionMethod = True if ls[5] == "True" else False
    secretKey = ls[7]
    pathIP = ls[8]
except:
    user = password = serverIndex = ipAddress = portNo = encryptionMethod = secretKey = pathIP = ""

layout = [
    [sg.Text('Login', size=(14,1)), sg.InputText(user, size=(36,1)), 
            sg.Text('Password', size=(14,1)), sg.InputText(password, password_char='*', size=(36,1))],
    [sg.Text("")],
    [sg.Text('Slot of radius:', size=(14,1)), sg.InputCombo((1, 2, 3), serverIndex, size=(34, 1)),
            sg.Text('', size=(14,1)), sg.RButton("Enable and Set Radius Server", size=(34, 1))],
    [sg.Text('IP Radius', size=(14,1)), sg.InputText(ipAddress, size=(36,1)),
            sg.Text('', size=(14,1)), sg.RButton("Check config Radius Server", size=(34, 1))],
    [sg.Text('Port №', size=(14,1)), sg.InputText(portNo, size=(36,1)),
            sg.Text('', size=(14,1)), sg.RButton("Disable Radius Server", size=(34, 1))],
    [sg.Text("Encryption Method:", size=(14,1)), sg.Radio('User', "RADIO1", default=True if encryptionMethod == True else False, size=(18,1)), 
            sg.Radio('CHAP', "RADIO1", size=(18,1), default=True if encryptionMethod == False else False)],
    [sg.Text('Secret Key', size=(14,1)), sg.InputText(secretKey, size=(36,1))],

    [sg.Text("")],
    [sg.Text("File IP", size=(14,1)), sg.InputText(pathIP, size=(72,1)), sg.FileBrowse(size=(14,1))],
    #[sg.Text('Console output')],
    #[sg.Output(size=(105, 30))],
    [sg.Text("", size=(88, None)), sg.Exit(size=(14,1))]
]

main_window = sg.Window('NEC Radius Server').Layout(layout)

layoutCheck = [
    [sg.Text('Console output')],
    [sg.Output(size=(105, 30))],
    [sg.Text("", size=(74, None)), sg.RButton("Start",size=(14,1)), sg.RButton("Back",size=(14,1))]
    ]

windowCheck = sg.Window('Check config Radius server').Layout(layoutCheck)
winCheckStatus = False

while True: 
    event, values = main_window.read()
    print(event, values) #debug

    user = str(values[0])
    password = str(values[1])
    serverIndex = str(values[2])
    ipAddress = str(values[3])
    portNo = str(values[4])
    encryptionMethod = "1" if values[5] == True else "2"
    secretKey = str(values[7])
    pathIP = str(values[8])

    if event in (None, 'Exit'):
        break
    elif event == "Enable and Set Radius Server":
        try:
            writeConfig(values)
            start(enableAndSetCongif, [user, password, serverIndex, ipAddress, portNo, encryptionMethod, secretKey, pathIP])
        except:
            print(sys.exc_info()[1])
    elif event == "Check config Radius Server":
        writeConfig(values)
        if not winCheckStatus:
            winCheckStatus = True
            try:
                while True:
                    eventCheck, values = windowCheck.Read()
                    if eventCheck == "Start":
                        start(checkConfig, [user, password, pathIP])
                    if eventCheck in (None, "Back"):
                        winCheckStatus = False
                        break
            except:
                print(sys.exc_info()[1])    
