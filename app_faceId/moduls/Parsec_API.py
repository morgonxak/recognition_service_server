'''
Класс взаимодействия с системой СКУД Parsec 3.0

Функционал:
    Запрос версии
    Запрос оргонизации
    Открыть сесию
    Получить список всех територий
    Отправить запрос на оборудовани
    Поиск сотрудника по ФИО
    Поиск сотрудника по индетификатору
    При откраки Уникального индетификатора возвращает код карты
    Получает информацию по уникальному ключу

Почта: cmit.dima@gmail.com
'''

import requests
import datetime
import xml.etree.ElementTree as ET

class prosecApi:
    '''
    Класс позволяет работать с оборудованием Фирмы Парсес
    '''
    headers = [{'content-type': 'application/soap+xml'}, {'Content-Type': 'text/xml'}]

    # Запрос версии
    GetVersion = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetVersion xmlns="http://parsec.ru/Parsec3IntergationService"/></soap:Body></soap:Envelope>"""
    # Запрос оргонизации
    GetDomains = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><GetDomains xmlns="http://parsec.ru/Parsec3IntergationService"/></soap12:Body></soap12:Envelope>"""
    #Открыть сесию
    OpenSessionRequest = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><OpenSession xmlns="http://parsec.ru/Parsec3IntergationService"><domain>{}</domain><userName>{}</userName><password>{}</password></OpenSession></soap12:Body></soap12:Envelope>"""#.format(domain, userName, password)
    # Получить список всех територий
    GetTerritoriesHierarhy = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><GetTerritoriesHierarhy xmlns="http://parsec.ru/Parsec3IntergationService"><sessionID>{}</sessionID></GetTerritoriesHierarhy></soap12:Body></soap12:Envelope>"""#.format(sessionId)
    #Отправить запрос на оборудовани
    SendHardwareCommand = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><SendHardwareCommand xmlns="http://parsec.ru/Parsec3IntergationService"><sessionID>{}</sessionID><territoryID>{}</territoryID><command>{}</command></SendHardwareCommand></soap12:Body></soap12:Envelope>"""#.format(sessionId, territoryId, comand)
    #Поиск сотрудника по ФИО
    FindPeople = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><FindPeople xmlns="http://parsec.ru/Parsec3IntergationService"><sessionID>{}</sessionID><lastname>{}</lastname><firstname>{}</firstname><middlename>{}</middlename></FindPeople></soap12:Body></soap12:Envelope>"""  # .format(sessionID, lastname, firstname, middlename)
    #Поиск сотрудника по индетификатору
    FindPersonByIdentifier = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><FindPersonByIdentifier xmlns="http://parsec.ru/Parsec3IntergationService"><sessionID>{}</sessionID><cardCode>{}</cardCode></FindPersonByIdentifier></soap12:Body></soap12:Envelope>"""#.format(sessionID, cardCode)
    #При откраки Уникального индетификатора возвращает код карты
    GetPersonIdentifiers = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><GetPersonIdentifiers xmlns="http://parsec.ru/Parsec3IntergationService"><sessionID>{}</sessionID><personID>{}</personID></GetPersonIdentifiers></soap12:Body></soap12:Envelope>"""#.format(sessionID, personID)
    #Получает информацию по уникальному ключу
    GetPerson = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetPerson xmlns="http://parsec.ru/Parsec3IntergationService"><sessionID>{}</sessionID><personID>{}</personID></GetPerson></soap:Body></soap:Envelope>"""#.format(sessionID, personID)


    def __init__(self, url, userName, password, domain):

        #Основные параметры
        self.url = url
        self.userName = userName
        self.password = password
        self.domain = domain
        #Глобальные парамеры
        self.session = None
        self.timeSession = None

        #Выводим Версию продукта
        response = self.__pull_request(self.GetVersion, self.headers[1])
        version = self.parsing_xml(response, 'varsion')
        print("Версия :", version)

    def __pull_request(self, request, headers=headers[0]):
        '''
        Отправляет запррос на сервер
        :param request:
        :return:
        '''
        request = request.encode('utf-8')
        response = requests.post(self.url, data=request, headers=headers)

        response = response.content.decode('UTF-8')
        #print(response)

        return response

    def parsing_xml(self, response, typeParsing):
        '''
        Парсим данные для разных ответов от сервера
        :param response: Ответ от сервера
        :param typeParsing:
        :return:
        '''
        root = ET.fromstring(response)
        if typeParsing == 'session':
            OpenSessionResult = root[0][0][0]
            Result = OpenSessionResult[0].text
            SessionID = OpenSessionResult[1][0].text
            #RootOrgUnitID = OpenSessionResult[1][1].text
            #RootTerritoryID = OpenSessionResult[1][2].text
            if Result == '0':
                return SessionID

        elif typeParsing == 'varsion':
            return root[0][0][0].text

        elif typeParsing == 'turnstile':
            return root[0][0][0].text

        elif typeParsing == 'get_info_user':
            peoples = {}
            for people in root[0][0][0]:
                idUser = people[0].text
                peoples[idUser] = {}
                peoples[idUser]['FIRST_NAME'] = people[1].text
                peoples[idUser]['LAST_NAME'] = people[2].text
                peoples[idUser]['MIDDLE_NAME'] = people[3].text
                peoples[idUser]['ORG_ID'] = people[5].text
            return peoples
        elif typeParsing == 'get_Person_Identifier':
            try:
                return root[0][0][0][0][0].text
            except IndexError:
                return ''
        elif typeParsing == 'get_info_on_cardID':
            peoples = {}
            try:
                key_people = root[0][0][0][0].text

                peoples[key_people] = {}
                peoples[key_people]['FIRST_NAME'] = root[0][0][0][1].text
                peoples[key_people]['LAST_NAME'] = root[0][0][0][2].text
                peoples[key_people]['MIDDLE_NAME'] = root[0][0][0][3].text
                peoples[key_people]['ORG_ID'] = root[0][0][0][5].text
                peoples[key_people]['cardID'] = ''
                return peoples
            except BaseException as e:
                print("Error parsing get_info_on_cardID: " + str(e))
                return ''

        elif typeParsing == 'get_photo_by_personID':
            people_info = {}
            try:
                key_personID = root[0][0][0][0].text
                people = root[0][0][0]

                people_info[key_personID] = {}
                people_info[key_personID]['FIRST_NAME'] = people[1].text
                people_info[key_personID]['LAST_NAME'] = people[2].text
                people_info[key_personID]['MIDDLE_NAME'] = people[3].text
                people_info[key_personID]['ORG_ID'] = people[5].text
                people_info[key_personID]['PHOTO'] = people[6].text
            except BaseException as e:
                return ''
            else:
                return people_info

    def __getSession(self):
        '''
        Получает новую сесию
        :return:
        '''

        request = self.OpenSessionRequest.format(self.domain, self.userName, self.password)
        response = self.__pull_request(request)
        self.session = self.parsing_xml(response, 'session')
        print("Получили новую сесию", self.session)
        self.timeSession = datetime.datetime.now()

    def __OpenSession(self):
        '''
        Получаем актуальную сесию
        :return:
        '''
        if self.session is None:
            print("Первый запуск программы, создаем сесию")
            self.timeSession = datetime.datetime.now()
            self.__getSession()
        else:
            delta = datetime.datetime.now() - self.timeSession
            if delta.seconds > 1*60:
                print("Количесво пройденного времяни", delta.seconds)
                self.__getSession()

    def getSession(self):
        '''
        Позволяет пользователю посмотреть на состояния сесии
        :return:
        '''
        self.__OpenSession()
        return self.timeSession, self.session

    def get_Person_Identifier(self, personID):
        '''
        Получает уникальный ключ карты по уникальному индентификатору
        :param personID:
        :return: CODE
        '''
        self.__OpenSession()
        request = self.GetPersonIdentifiers.format(self.session, personID)
        response = self.__pull_request(request, self.headers[0])
        Result = self.parsing_xml(response, 'get_Person_Identifier')

        return Result

    def get_info_user(self, lastname='', firstname='', middlename=''):
        '''
        Получает информацию о пользователе
        :param lastname:
        :param firstname:
        :param middlename:
        :return: {'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49': {'FIRST_NAME': 'Дмитрий', 'LAST_NAME': 'Шумелев', 'MIDDLE_NAME': 'Игоревич', 'ORG_ID': 'd186ffeb-3499-4eb3-844e-cb3f2f7f97fb'}}
        '''

        self.__OpenSession()
        request = self.FindPeople.format(self.session, lastname, firstname, middlename)
        response = self.__pull_request(request, self.headers[0])

        Result = self.parsing_xml(response, 'get_info_user')

        return Result

    def get_info_on_cardID(self, cardID):
        self.__OpenSession()
        request = self.FindPersonByIdentifier.format(self.session, cardID)
        response = self.__pull_request(request, self.headers[1])
        Result = self.parsing_xml(response, 'get_info_on_cardID')

        return Result

    def get_data_info_cardID(self, lastname='', firstname='', middlename=''):
        '''
        Дополняет функцию get_info_user и возвращает масив с дополнительном пораметром cardID
        :param lastname:
        :param firstname:
        :param middlename:
        :return: {'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49':
        {'FIRST_NAME': 'Дмитрий', 'LAST_NAME': 'Шумелев', 'MIDDLE_NAME': 'Игоревич', 'ORG_ID': 'd186ffeb-3499-4eb3-844e-cb3f2f7f97fb', 'cardID': '004EF89D'}}
        '''
        dict_check = self.get_info_user(lastname, firstname, middlename)
        Result = {}
        for key_people in dict_check:
            print(key_people)
            Result[key_people] = {}
            Result[key_people]['FIRST_NAME'] = dict_check[key_people]['FIRST_NAME']
            Result[key_people]['LAST_NAME'] = dict_check[key_people]['LAST_NAME']
            Result[key_people]['MIDDLE_NAME'] = dict_check[key_people]['MIDDLE_NAME']
            Result[key_people]['ORG_ID'] = dict_check[key_people]['ORG_ID']
            Result[key_people]['cardID'] = self.get_Person_Identifier(key_people)

        return Result

    def get_photo_by_personID(self, personID):
        '''
                Получает информация о пользователе
                :param personID:
                :return: {'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49': {'FIRST_NAME': '', 'LAST_NAME': '', 'MIDDLE_NAME': '', 'ORG_ID': '', 'PHOTO': 'Bace64'}}
                '''
        self.__OpenSession()
        request = self.GetPerson.format(self.session, personID)
        response = self.__pull_request(request, self.headers[1])
        Result = self.parsing_xml(response, 'get_photo_by_personID')

        return Result

    sideOpen = {"entrance": 1, 'exit': 2}
    territoryId = 'c94830ab-2c17-4230-9561-4717cd98e207'

    def open_turnstile(self, comand, territoryId=territoryId):
        '''
        Открытия турникета на вход или на выход в зависимости от sideOpen
        :param comand:
        :return:
        '''
        self.__OpenSession()
        request = self.SendHardwareCommand.format(self.session, territoryId, comand)
        response = self.__pull_request(request)
        Result = self.parsing_xml(response, 'turnstile')
        return Result


if __name__ == '__main__':
    #Пример работы

    url = "http://82.179.15.125:10101/IntegrationService/IntegrationService.asmx"
    #domain = '\xd0\x9a\xd0\xb5\xd0\xbc\xd0\x93\xd0\xa3'
    domain = 'КемГУ'
    userName = 'test'
    password = '123456'

    test = prosecApi(url, userName, password, domain)
    #Получить сесию
    #s = test.getSession()
    #ОТкрыть турникет на вход
    #test.open_turnstile(test.sideOpen['entrance'])
    #Поиск пользователя по ФИО
    # res = test.get_info_user('Шумелев')
    # res = test.get_data_info_cardID('Шуме')
    #res = test.get_info_on_cardID('004EF89D')
    #print(res)
    #Получения индетификатора пользователя по ключу пользователя
    # tt=test.get_photo_by_personID('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49')
    #tt=test.get_photo_by_personID('ff4e0b2f-1b2f-430e-9efc-6fa00b5a8f9a')
    tt=help(test)

    print(tt)