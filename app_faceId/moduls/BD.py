'''
Модуль предназначен для взамодействия с базой данных PostgreSQL
Функционал:
    pushData
    pushData_by_web
    del_user
    del_user
    getData_by_person_id
    getData_by_person_id_by_web
    get_all_Users_Info
    get_all_data
    convert_base64_to_image
    convert_image_base64
    get_number_of_users
    get_number_of_users_web
    pull_event

Почта: cmit.dima@gmail.com
'''

import psycopg2
import base64
import numpy as np
import cv2
import uuid

class BD:
    def __init__(self, dict_connect_settings):
        #Соеденения с базой данных
        try:
            self.con = psycopg2.connect(
                database=dict_connect_settings['database'],
                user=dict_connect_settings['user'],
                password=dict_connect_settings['password'],
                host=dict_connect_settings['host'],
                port=dict_connect_settings['port'])
        except BaseException as e:
            raise ValueError("Error connect BD: " + str(e))

        try:
            self.cur = self.con.cursor()
        except BaseException as e:
            raise ValueError("Error create cursor " + str(e))

    def pushData(self, card_id_code, person_id, full_name, photo_rgb_base64, descriptor):
        '''
        ОТправляет данные в базу
        :param card_id_code: никальная карта пользователя
        :param full_name: ФИО пользователя
        :param photo_rgb: Фото пользователя
        :return:
        '''
        try:

            if len(self.getData_by_person_id(person_id)) == 0:
                print("добовляем пользователя")
                #Если пользовавателя нету то добовляем
                self.cur.execute(
                    "INSERT INTO user_bd (card_id_code, person_id, full_name, photo_rgb, descriptor_rgb) VALUES ('{}','{}','{}','{}','{}')".format(
                        card_id_code, person_id, full_name, photo_rgb_base64, descriptor)
                )
                self.con.commit()
            else:
                #Обновить данные пользователя
                print("Изменяем пользователя")
                if photo_rgb_base64 == '':
                    self.cur.execute(
                        "Update user_bd set card_id_code = ('{}'), full_name = ('{}'), descriptor_rgb = ('{}') where person_id = '{}'".format(
                            card_id_code, full_name, descriptor, person_id))
                else:
                    self.cur.execute(
                        "Update user_bd set card_id_code = ('{}'), full_name = ('{}'), photo_rgb = ('{}'), descriptor_rgb = ('{}') where person_id = '{}'".format(
                            card_id_code, full_name, photo_rgb_base64, descriptor, person_id))
                self.con.commit()

        except BaseException as e:
            raise ValueError("Error sending to database: " + str(e))
        return 0

    def pushData_by_web(self, person_id, last_name, first_name, middle_name, photo_rgb_base64, descriptor, post):
        '''
        ОТправляет данные в базу
        :param card_id_code: никальная карта пользователя
        :param full_name: ФИО пользователя
        :param photo_rgb: Фото пользователя
        :return:
        '''
        try:

            if len(self.getData_by_person_id_by_web(person_id)) == 0:
                print("добовляем пользователя")
                #Если пользовавателя нету то добовляем
                self.cur.execute(
                    "INSERT INTO web_user (person_id, last_name, first_name, middle_name, photo_rgb, descriptor_rgb, post) VALUES ('{}','{}','{}','{}','{}', '{}', '{}')".format(
                        person_id, last_name, first_name, middle_name, photo_rgb_base64, descriptor, post)
                )
                self.con.commit()
            else:
                #Обновить данные пользователя
                print("Изменяем пользователя")
                if photo_rgb_base64 == '':
                    self.cur.execute(
                        "Update web_user set last_name = ('{}'), first_name = ('{}'), middle_name = ('{}'), post = ('{}') where person_id = '{}'".format(
                            last_name, first_name, middle_name, post))

                elif photo_rgb_base64 != '':
                    self.cur.execute(
                        "Update web_user set last_name = ('{}'), first_name = ('{}'), middle_name = ('{}'), post = ('{}'), photo_rgb = ('{}') where person_id = '{}'".format(
                            last_name, first_name, middle_name, post, photo_rgb_base64))

                self.con.commit()

        except BaseException as e:
            raise ValueError("Error sending to database: " + str(e))
        return 0

    def del_user(self, person_id):
        '''
        Удаляет пользователя
        :param person_id:
        :return:
        '''
        print(person_id)
        try:

                self.cur.execute("DELETE FROM user_bd where person_id = '{}'".format(person_id))
                #print(rows)
                self.con.commit()

        except BaseException as e:
            return "Error get Users info: " + str(e)
        else:
            return 0

    def getData_by_person_id(self, person_id):
        '''
        Получает информацию по индитификатору пользователя
        :param person_id: 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49'
        :return: [('004EF89D', 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49', 'Шумелев Дмитрий Игоривич')]
        '''
        try:
            self.cur.execute("SELECT card_id_code, person_id, full_name FROM user_bd WHERE person_id = '{}'".format(person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def getData_by_person_id_by_web(self, person_id):
        '''
        Получает информацию по индитификатору пользователя
        :param person_id: 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49'
        :return: [('004EF89D', 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49', 'Шумелев Дмитрий Игоривич')]
        '''
        try:
            self.cur.execute("SELECT person_id, last_name, first_name, middle_name, post FROM web_user WHERE person_id = '{}'".format(person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def get_all_Users_Info(self):
        '''
        Получить список всех пользователей в системе
        :return: list : card_id_code, person_id, full_name, person_id
        '''
        try:
            self.cur.execute("SELECT card_id_code, person_id, full_name, person_id from user_bd")

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def get_all_data(self):
        '''
        Получаем все данные включая фотографии пользователей
        :return:
        '''
        try:
            self.cur.execute("SELECT card_id_code, full_name, photo_rgb, person_id from user_bd")

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def __convert_image_base64(self, pathImage):
        '''
        Конвертируем изображения для добавления в базу
        :return:
        '''
        try:
            image = open(pathImage, 'rb')  # open binary file in read mode
            image_read = image.read()
            image_64_encode = base64.encodebytes(image_read)
        except BaseException as e:
            raise ValueError("Error convert image base64: " + str(e))
        else:
            return image_64_encode.decode("utf-8")

    def __convert_base64_to_image(self, image_base64) -> np.ndarray:
        '''
        Конвертируем из базы из Base64 в формат numpy изображения
        :return:
        '''
        try:
            image = base64.decodebytes(image_base64)
            nparr = np.frombuffer(image, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except BaseException as e:
            raise ValueError("Error convert base64 to image: " + str(e))
        else:
            return img_np

    def convert_base64_to_image(self, image_base64):
        return self.__convert_base64_to_image(image_base64)

    def convert_image_base64(self, pathImage):
        '''
        Конвертируем изображения для добавления в базу
        :return:
        '''
        return self.__convert_image_base64(pathImage)

    def get_number_of_users(self):
        '''
        Получить количество пользователей загружены в базу
        :return:
        '''
        try:
            #SELECT count(*) FROM my_table
            self.cur.execute("SELECT count(*) FROM user_bd")

            rows = self.cur.fetchall()[0][0]

        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def get_number_of_users_web(self):
        '''
        Получить количество пользователей загружены в базу
        :return:
        '''
        try:
            #SELECT count(*) FROM my_table
            self.cur.execute("SELECT count(*) FROM web_user")

            rows = self.cur.fetchall()[0][0]

        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def pull_event(self, dict_data):
        '''
        Добовляет данные событий
        :param dict_data:
        :return:
        '''
        try:
            self.cur.execute(
                "INSERT INTO visits (person_id, time_event, events, event_source, subject, summary) VALUES ('{}','{}','{}','{}', '{}', '{}')".format(
                    dict_data['person_id'], dict_data['time_event'], dict_data['events'], dict_data['event_source'], dict_data['subject'], dict_data['summary'])
            )
            self.con.commit()
        except BaseException as e:
            print("error", e)

    # def get_latest_version(self):
    #     '''
    #     Получает последнюю версию классификатора
    #                version_classification,                              changes,                               path_classification
    #     :return:  (1,                      'Обученный на 50 фотографиях каждого человека в базе 614 человек', 'data/classificators/1')
    #     '''
    #     try:
    #         #SELECT version_classification, changes, path_classification FROM classification WHERE person_id = MAX (version_classification)
    #         #SELECT MAX (version_classification) from classification UNION SELECT version_classification, changes, path_classification from classification
    #
    #         self.cur.execute("SELECT MAX (version_classification) from classification")
    #         max_version_classification = self.cur.fetchall()
    #
    #         self.cur.execute("SELECT version_classification, changes, path_classification FROM classification WHERE version_classification = {}".format(max_version_classification[0][0]))
    #         rows = self.cur.fetchall()
    #
    #     except BaseException as e:
    #         raise ValueError("Error get Users info: " + str(e))
    #     else:
    #         return rows[0]

    def __get_descriptors_by_personId(self, person_id, name_table):
        '''
        Получает все дескрипторы для пользователя для определенный базы
        :param person_id:
        :return:
        '''
        try:
            self.cur.execute("SELECT person_id, descriptor_rgb FROM {} WHERE person_id = '{}'".format(name_table, person_id))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def get_descriptors_by_personId_web(self, person_id):
        '''

        :param person_id:
        :return:
        '''
        return self.__get_descriptors_by_personId(person_id, 'web_user')

    def get_descriptors_by_personId_student(self, person_id):
        '''
        Получаем данные для пользователя
        :param person_id:
        :return:
        '''
        return self.__get_descriptors_by_personId(person_id, 'user_bd')[0]

    def __get_all_users_for_table(self, name_table):
        '''
                Получаем все данные включая фотографии пользователей
                :return:
                '''
        try:
            self.cur.execute("SELECT person_id from {}".format(name_table))

            rows = self.cur.fetchall()
        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows

    def get_all_personId_for_web(self):
        '''

        :return:
        '''
        return self.__get_all_users_for_table('web_user')

    def get_all_personId_for_students(self):
        '''

        :return:
        '''
        return self.__get_all_users_for_table('user_bd')

    def get_latest_version(self, mode):
        '''
        Получает последнюю версию классификатора
        :return:
        version_classification - Версия классификатора
        changes - Описание
        path_classification - путь
        data_time - время создания
        uuid - Уникальный имя
        '''
        try:
            self.cur.execute("SELECT version_classification, changes, path_classification, data_time, uuid "
                             "FROM classification "
                             "WHERE mode_classification = {} "
                             "ORDER BY data_time DESC".format(mode))
            rows = self.cur.fetchall()

        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:
            return rows[0]

    def pull_now_version(self, version_classification, changes, path_classification, data_time, uuid, mode):
        '''
        Отправляет данные в базу
        :param version_classification: вевсия классификатора
        :param changes: Описание изменений
        :param path_classification: относительный путь
        :param data_time: время создание классификатора
        :param uuid: уникальный идентификатор
        :param mode: для кого служит классификатор
        :return:
        '''
        try:

            self.cur.execute(
                "INSERT INTO classification (version_classification, changes, path_classification, data_time, uuid, mode_classification) "
                "VALUES ('{}','{}','{}','{}' ,'{}' ,'{}')".format(
                    version_classification, changes, path_classification, data_time, uuid, mode)
            )
            self.con.commit()

        except BaseException as e:
            raise ValueError("Error sending to database: " + str(e))
        return 0

    def get_version_by_uuid(self, uuid_classification):
        '''
        Получаем информацию о классификаторе по его уникальному ключю
        :param uuid_classification:
        :return:
        '''
        try:
            self.cur.execute(
                "SELECT version_classification, changes, path_classification, data_time, uuid FROM classification WHERE uuid = '{}'".format(uuid_classification))

            rows = self.cur.fetchall()

        except BaseException as e:
            raise ValueError("Error get Users info: " + str(e))
        else:

            return rows

    def get_now_uuid(self):
        '''
        Генерирует новый уникальный идентификатор и проверяет что бы небыло совподений
        :return:
        '''
        uuid_now = uuid.uuid4()

        if len(self.get_version_by_uuid(uuid_now)) == 0:
            return uuid_now
        else:
            return uuid.uuid4()


dict_connect_settings = {"database": "faceid",
                         "user": "dima",
                         "password": "asm123",
                         "host": "127.0.0.1",
                          "port": "5432"}

if __name__ == '__main__':
    obj_BD = BD(dict_connect_settings)
    version_0 = obj_BD.get_latest_version(0)
    version_1 = obj_BD.get_latest_version(1)
    print(version_0)
    print(version_1)

    #obj_BD.pushData('sda','re','ads,',r'/home/dima/PycharmProjects/fase_idTest/fase/1.jpg',r'/home/dima/PycharmProjects/fase_idTest/fase/1.jpg')
    #info_by_person_id = obj_BD.getData_by_person_id('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49')
    #print(info_by_person_id)
      # image = obj_BD.convert_base64_to_image(q.encode())
    # print(image)
    # cv2.imwrite('image.png', image)
    # list_Users = obj_BD.getUserInfo()
    # for user in list_Users:
    #     print(user)
    #card_id_code, person_id, full_name, photo_rgb_path, photo_3d_path, photo_old
    # obj_BD.pushData('sadw', 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e492', 'sadsad', 'None', 'None', 'None')
    #
    # ttt = obj_BD.getData_by_person_id('b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e492')
    # dict_data = {}
    # dict_data['person_id'] = "b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e492"
    # dict_data['time_event'] = "2020-03-14 16:58:48.045317"
    # dict_data['events'] = "Открытия двери"
    # dict_data['event_source'] = "ТЕстовая дверь"
    # dict_data['subject'] = "тест"
    # dict_data['summary'] = "тест"
    #
    # obj_BD.pull_event(dict_data)
    # ttt = obj_BD.get_number_of_users()
    # print(ttt)
    #print(ttt)