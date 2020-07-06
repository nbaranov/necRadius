import requests

from ast import literal_eval
from bs4 import BeautifulSoup as bs
from functions import logAndPrint


class nec():
    '''Класс для работы с РРЛ NEC'''


    def __init__(self, ip, login, password):
        '''Авторизация на узле NEC создает сессию из requests и получает session id для последующих запросов '''
        
        self.login = login
        self.url = f'http://{ip}/cgi/lct.cgi'
        self.headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'LCT_POLLTIME=NONE',
        'Referer' : self.url
        }
        logAndPrint(f"Подключаюсь к элементу {ip}", "", 0)
        # get session id first step authentication
        self.session = requests.session()
        postData = {'CGI_ID': 'GET_LCT01000000_01', 'userName': self.login, 'password': password}
        auth = self.post(postData, 50)
        soup = bs(auth.text, "html.parser")
        self.sessionID = int(soup.find(id = "LCTSESSIONID").get('value'))

        # second step authentication 
        postData = {'CGI_ID': 'GET_LCT01000000_02', 'USER_NAME': self.login,'SESSION_ID': self.sessionID}
        self.post(postData, timeout = 50)

        # third step authentication posts
        postData = {'CGI_ID': 'GET_LCT01000000_03', 'userName': self.login,'SESSION_ID': self.sessionID}
        self.post(postData, timeout = 50)

        # fourth step authentication posts
        postData = {'CGI_ID': 'GET_LCT01000000_04', 'USER_NAME': self.login,'SESSION_ID': self.sessionID}
        self.post(postData, timeout = 50)

        # fifth step authentication posts
        postData = {'CGI_ID': 'GET_LCT01000000_05', 'userName': self.login,'SESSION_ID': self.sessionID}
        response = self.post(postData, timeout = 50)
        if self.checkStatus(response) == False:
            logAndPrint(f"Не удалось авторизоваться на сетевом элементе{ip}")
            raise SystemError("Не удалось авторизоваться на сетевом элементе")

        # sixth step authentication posts
        postData = {'CGI_ID': 'GET_LCT99010100_01', 'loginuser': self.login, 'USER_NAME': self.login,'SESSION_ID': self.sessionID}
        response = self.post(postData, timeout = 50)
        if self.checkStatus(response) == False:
            logAndPrint(f"Не удалось авторизоваться на сетевом элементе{ip}")
            raise SystemError("Не удалось авторизоваться на сетевом элементе")
        logAndPrint("Авторизация успешно пройдена")


    def post(self, postData, timeout = 30):
        '''Делает post запрос на сетевой элемент с переданными в него post data'''
        response = self.session.post(url = self.url, data = postData, headers = self.headers, timeout = timeout)
        return response


    def checkStatus(self, response):
        '''Проверяет cgi статус ответа узла, если он "0" то есть все ок, возвращает True иначе False'''
        if int(literal_eval(response.text)['status'][0]['cgi_status']) == 0:
            return True
        return False


    def checkConfigRadius(self):
        '''Запрашивает и печатет в консоль и лог файл параметры Радиус сервера на элементе'''
        lis = self.getRadiusSet()
        for i in range(len(lis)):
            dic = lis[i]
            logAndPrint(f'Параметры радиус сервера сервера строка {i+1}: IP: {dic["ipAddress"]}, port: {dic["portNo"]}, encription: {"CHAP" if dic["encryptionMethod"] == "2" else "User"}, Secret Key: "{dic["secretKey"]}"')


    def turnOnRadius(self):
        '''Включает Радиус сервер на сетевом элементе
        \nНичего не возвращает, результат выводит в консоль'''    
        postData = {
        'CGI_ID': 'SET_LCT09RAD001_05', 
        'LIST': '[{"index":"1","radiusAuthMethod":"3","radiusAuthSequence":"2"}]', 
        'LIST_COUNT': 1, 
        'USER_NAME': self.user,
        'SESSION_ID': self.sessionid
        }
        response = nec.post(postData, timeout = 20)
        if self.checkStatus(response):
            logAndPrint("Радиус сервер успешно включен")
        else:
            logAndPrint("Произошла ошибка при включении радиус сервера")


    def checkStatusRadius(self):
        '''Проверяет статус радиус сервера на элементе.
        \n Возвращает значение:
        \nTrue - сервер включен
        \nFalse - сервер выключен'''
        postData = {'CGI_ID': 'GET_LCT09RAD001_01', 'USER_NAME': self.user, 'SESSION_ID': self.sessionid}
        response = session.post(url, headers = headers, data = postData, timeout = 20)
        dic = literal_eval(response.text)
        gsiStatus = int(dic['data'][0]['authentication'][0]['radiusAuthMethod'])
        if gsiStatus ==  3:
            return True
        else: 
            return False   


    def setParamRadius(self, params):
        '''Устанавливает параметры радиус сервера переданные в словаре в виде:
        \n {"serverIndex" = "1", - номер строки параметров от 1 до 3
        \n "ipAddress" = "0.0.0.0", - IP адрес радиус сервера
        \n "portNo" = "1234", - номер порта
        \n "encryptionMethod" = "1", - где 1 - User, 2 - CHAP
        \n "secretKey" = "secret"} - Секретный ключ для подключения к серверу
        \n Возвращает True если параметры установлены успешно или False в противном случае
        '''
        postData = {
        'CGI_ID': 'SET_LCT09RAD002_05', 
        'LIST': f'{params}',
        'LIST_COUNT': 1,
        'USER_NAME': self.user,
        'SESSION_ID': self.sessionID
        }
        response = self.post(postData, timeout = 20)
        return checkStatus(response)   


    def getRadiusSet(self):
        '''Получить настройки радиус сервера на элементе
        \nВозвращает список словарей с настройками'''
        postData = {'CGI_ID': 'GET_LCT09RAD002_01', 'USER_NAME': self.login,'SESSION_ID': self.sessionID}
        response = self.post(postData, timeout = 20)
        response = literal_eval(response.text) 
        radiusSet = response['data'][0]['radiusRadiusServer']
        return radiusSet
