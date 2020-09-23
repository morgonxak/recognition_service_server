'''
Модуль предназначен для запуска всех компонентов при старте программы

Почта: cmit.dima@gmail.com
'''

import os
import cv2

from app_faceId.moduls.BD import BD
from app_faceId import app
from app_faceId.moduls.Parsec_API import prosecApi
from app_faceId.moduls.API.pull_data_client import server_pull_data
from app_faceId.moduls.trening_models_cvm_knn import class_training

import pickle

class init_components:
    '''
    служит для
    - обновления данных пользователей
    - формирование данных для распознование
    '''
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        dict_connect_settings = {"database": app.config['name_dataBase'],
                                 "user": app.config['login_DB'],
                                 "password": app.config['password_DB'],
                                 "host": app.config['IP_DB'],
                                 "port": app.config['PORT_DB']}

        self.BD = BD(dict_connect_settings)

        self.parsec_api = prosecApi(app.config['url_parsec'], app.config['user_parsec'], app.config['password_parsec'], 'КемГУ')
        self.get_latest_version()

        print(app.config['IP_Server'], app.config['PORT_server_pull_data'])
        self.server_pull_data = server_pull_data(app.config['IP_Server'], app.config['PORT_server_pull_data'])
        self.server_pull_data.name = "thread_server_pull_data"
        self.server_pull_data.start()

        self.thread_trening = class_training()
        self.thread_trening.name = 'thread_trening'
        self.thread_trening.start()

    def get_latest_version(self):
        '''
        Получить последнюю версию классификатора
        :return:
        '''

        version = self.BD.get_latest_version(1)
        path_svm_model = os.path.join(app.config['path_dir_calassificator'], version[2], 'cvm_model.pk')
        path_knn_model = os.path.join(app.config['path_dir_calassificator'], version[2], 'knn_model.pk')

        self.model_cvm = pickle.load(open(path_svm_model, 'rb'))
        self.model_knn = pickle.load(open(path_knn_model, 'rb'))


    ##############!!!!!!!!!!!!!!!!!Надо поправить Изменилась
    def updateDB(self):
        '''
        Обновляет данные в базе из папке
        :return:
        '''
        list_person_id = os.listdir(app.config['path_photo'])
        for person_id in list_person_id:
            path_photo_rgb = os.path.join(app.config['path_photo'], person_id, 'RGB', 'photo.png')
            path_photo_rgb_save = os.path.join(app.config['path_photo'], person_id, 'RGB', 'photo_old.png')

            info_user = self.parsec_api.get_photo_by_personID(person_id)

            print(info_user)


            FIRST_NAME = info_user[person_id]['FIRST_NAME']
            LAST_NAME = info_user[person_id]['LAST_NAME']
            MIDDLE_NAME = info_user[person_id]['MIDDLE_NAME']
            ORG_ID = info_user[person_id]['ORG_ID']
            PHOTO = info_user[person_id]['PHOTO']

            print(FIRST_NAME, LAST_NAME, MIDDLE_NAME, ORG_ID, person_id, path_photo_rgb, path_photo_rgb_save)

            image_photo_old = self.BD.convert_base64_to_image(PHOTO.encode())
            cv2.imwrite(path_photo_rgb_save, image_photo_old)

            #photo_rgb_base64 = self.BD.convert_image_base64(path_photo_rgb)

            #card_id_code, person_id, full_name, photo_rgb_path, photo_3d_path, photo_old

            full_name = "{} {} {}".format(LAST_NAME, FIRST_NAME, MIDDLE_NAME)
            self.BD.pushData('None', person_id, full_name, path_photo_rgb)



if __name__ == '__main__':
    import time

    old_time = time.time()

    print("time:", time.time() - old_time)