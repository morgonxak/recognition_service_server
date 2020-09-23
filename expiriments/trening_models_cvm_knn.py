'''
Модуль предназначен для создания классификаторов CVM и KNN по фотографиям из базы данных
'''

import face_recognition
from sklearn import svm
import os
import pickle
import time
import math
import time
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
import psycopg2
import numpy as np
from face_recognition.face_recognition_cli import image_files_in_folder
import threading
dict_connect_settings = {"database": "faceid",
                         "user": "dima",
                         "password": "asm123",
                         "host": "127.0.0.1",
                          "port": "5432"}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
encodings = []  # 128 уникальных признаков
person_id = []  # Уникальный ключ пользователя


def train_cvm():
    '''
    Тренировка cvm классификатора
    :return:
    '''
    clf_svm = svm.SVC(gamma='scale')
    clf_svm.fit(encodings, person_id)
    return clf_svm

def train_knn(n_neighbors=None, knn_algo='ball_tree'):
    # Определите, сколько соседей использовать для взвешивания в классификаторе KNN
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(encodings))))

    clf_knn = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    clf_knn.fit(encodings, person_id)
    return clf_knn

def load_image(path_Image, person):
    '''
    Загружаем изображения в память и формируем базу для обучения
    :param path_Image:
    :param person:
    :return:
    '''
    image = face_recognition.load_image_file(path_Image)
    face_bounding_boxes = face_recognition.face_locations(image)

    if len(face_bounding_boxes) != 1:
        # если изображения не подходит.
        print("Изображение {} не может учавствовать в трененровки: {}".format(path_Image, "Нет лица" if len(face_bounding_boxes) < 1 else "Более одного лица"))
    else:
        # Доболяем изображения
        print("Изображения добавлено: ", path_Image)
        encodings.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
        person_id.append(person)

def save_model(clf, path_save):
    '''
    Сохраняет данные обучения
    :param clf:
    :param path_save:
    :return:
    '''
    with open(path_save, 'wb') as f:
        pickle.dump(clf, f)

    return path_save

def save_BD_signs(path_save):
    '''
    Сохраняем базу данных признаков для переобучения
    :param path_save:
    :return:
    '''
    data = [encodings, person_id]
    with open(path_save, 'wb') as f:
        pickle.dump(data, f)

    return path_save

def load_BD_signs(path_pl):
    encodings, person_id = pickle.load(open(path_pl, 'rb'))

    return encodings, person_id

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

def main(path_BD, path_save_clf, pref='v2', dir_photo = 'photo_RGB'):
    '''
    Проходит по всем фотографиям и загружает данные после тренировка
    :param path_BD:
    :return:
    '''
    global encodings, person_id
    train_dir = os.listdir(path_BD)
    print("В тренировке учавствуют количество людей:", len(train_dir))
    old_time_load_data = time.time()

    for count_key, person in enumerate(train_dir):
        path_person = os.path.join(path_BD, person, dir_photo)

        pix = os.listdir(path_person)
        print("Начало загрузки фотографий для:", person)
        print("Номерн пользователя:", count_key)
        print("Количество фотографий:", len(pix))
        print("Путь до фотографий:", path_person)

        for person_img in pix:
            path_image_person = os.path.join(path_person, person_img)

            #Проверяем изображения на формат и на присутствие
            if not os.path.isfile(path_image_person) or os.path.splitext(path_image_person)[1][1:] not in ALLOWED_EXTENSIONS:
                raise Exception("Invalid image path: {}".format(path_image_person))

            load_image(path_image_person, person)

    print("Загрузка данных завершена", time.time() - old_time_load_data)

    #Обучаем нейросеть
    print('обучаем нейросети')
    clf_svm = train_cvm()
    clf_knn = train_knn()
    print("обучение завершено")
    #Сохраняем данные
    # save_model(clf_svm, os.path.join(path_save_clf, "svm_model_"+pref+'.pk'))
    # save_model(clf_knn, os.path.join(path_save_clf, "knn_model_"+pref+'.pk'))

    save_BD_signs(r'/home/dima/PycharmProjects/fase_idTest/app_faceId/models/bd' + pref + '.pl')



if __name__ == '__main__':
    #path_BD = r'/media/dima/d/PhotoBD'
    # path_BD = r'/media/dima/d/test_model'
    path_save_clf = r'/home/faceid/paceID_server/expiriments'

    encodings, person_id = load_BD_signs(r'/home/faceid/paceID_server/data/DB_users/bdv3.pl')

    print('обучаем нейросети')
    clf_svm = train_cvm()
    clf_knn = train_knn()
    print("обучение завершено")

    pref = '12'
    save_model(clf_svm, os.path.join(path_save_clf, "svm_model_"+pref+'.pk'))
    save_model(clf_knn, os.path.join(path_save_clf, "knn_model_"+pref+'.pk'))

    # data = {}
    # for count, i in enumerate(zip(person_id, encodings)):
    #     if data.get(i[0], None) is None:
    #         data[i[0]] = []
    #         data[i[0]].append(i[1].tolist())
    #     else:
    #         data[i[0]].append(i[1].tolist())
    #
    #     if count % 4 == 0:
    #         print("Первый шаг:", count)

    import json

    #obj_db = BD(dict_connect_settings)

    # for count, person_id in enumerate(data):
    #
    #     descriptor = data[person_id]
    #
    #     infoUser = obj_db.getData_by_person_id(person_id)
    #
    #     card_id_code = infoUser[0][0]
    #     person_id = infoUser[0][1]
    #     full_name = infoUser[0][2]
    #
    #     obj_db.pushData("None", person_id, full_name, '', descriptor)
    #
    #     if count % 4 == 0:
    #         print("Осталось:", len(data) - count)
    #
    # with open("data_file.json", "w") as write_file:
    #     json.dump(data, write_file)
    # print("VSE")
    #main(path_BD, path_save_clf, pref='v3', dir_photo='photo_RGB')




























