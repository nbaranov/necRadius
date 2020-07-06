import datetime
import openpyxl


def timenow():
    '''возвращает текущие дату и время в формате DD.MM.YYYY HH:MM:SS'''
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def readFileIP(path):
    '''читает IP адреса из файла выгрузки Сканера программы NetSetMan'''
    ipList = []
    with open(path, 'r', encoding='utf_16_le') as inFile:
        for line in inFile:
            line = line.strip(" \n")
            if line[0] == ";":
                ipList.append(line.split(";")[1])
    return ipList


def logAndPrint(massage, ind="\t\t   ", dateform=-8):
    '''выводит ссобщение в консоль и файл логов
    \n Первую строку вывести с параметрами "ind = "" deteform = 0"
    в результате получит полную дату и время без смещения, 
    а пареметры по умолчанию отрезают дату и сдвигают запись'''
    date = timenow()[dateform:]
    print(f"{ind}{massage}")
    with open('logs.log', 'a', encoding="UTF-8") as logs:
        logs.write(f'{ind}{date} {massage}\n')

def readIPfromXLSX():
    '''читает IP адреса из .xslx  файла таблицы скопированной
    с сайта Смирнова. IP адреса в столбце F читает 2500 строк'''
    wb = openpyxl.open("NEnec.xlsx")
    lis = wb.sheetnames
    sheet = wb[lis[0]]

    ip_list = [v[0].value for v in sheet['F1:F2500']]
    for i in range(len(ip_list) - 1, -1, -1):
        if ip_list[i] == None:
            ip_list.pop(i)
    
    return ip_list

