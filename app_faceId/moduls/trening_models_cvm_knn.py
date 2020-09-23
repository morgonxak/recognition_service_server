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
from app_faceId import app
import datetime


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class class_training(threading.Thread):
    '''
    Класс для создания классификатора новой версии
    Когда создовать:
    1)по истечению времени
    2)по сигналу из вне
    '''
    def __init__(self):
        super().__init__()

        self.encodings = []  # 128 уникальных признаков
        self.person_id = []  # Уникальный ключ пользователя

        self.status_threading = True  #Статус потока
        self.status_trening = False
        self.mode = {'web_user': [0, False], 'studets': [1, False]}

    def __train_cvm(self):
        '''
        Тренировка cvm классификатора
        :return:
        '''
        clf_svm = svm.SVC(gamma='scale')
        clf_svm.fit(self.encodings, self.person_id)
        return clf_svm

    def __train_knn(self, n_neighbors=None, knn_algo='ball_tree'):
        # Определите, сколько соседей использовать для взвешивания в классификаторе KNN
        if n_neighbors is None:
            n_neighbors = int(round(math.sqrt(len(self.encodings))))

        clf_knn = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        clf_knn.fit(self.encodings, self.person_id)
        return clf_knn

    @staticmethod
    def image_to_descriptor(image):
        '''
        Получает изображения и отдает дескриптор
        :param image_mat:
        :return:
        '''
        face_bounding_boxes = face_recognition.face_locations(image)

        if len(face_bounding_boxes) != 1:
            # если изображения не подходит.
            print("Изображение не может учавствовать в трененровки: {}".format("Нет лица" if len(
                face_bounding_boxes) < 1 else "Более одного лица"))
            return None
        else:
            # Доболяем изображения

            return face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0]

    def load_image(self, path_Image, person):
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
            self.encodings.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
            self.person_id.append(person)

    def __save_model(self, clf, path_save):
        '''
        Сохраняет данные обучения
        :param clf:
        :param path_save:
        :return:
        '''
        with open(path_save, 'wb') as f:
            pickle.dump(clf, f)

        return path_save

    def __get_descriptors_for_students(self):
        '''
        Получить encodings, person_id для обучения
        :return: encodings, person_id
        '''

        encodings = []
        person_id = []

        listUsers = app.config['components_obj'].BD.get_all_personId_for_students()

        for personId in listUsers:
            descriptors = app.config['components_obj'].BD.get_descriptors_by_personId_student(personId[0])
            try:
                for descriptor in descriptors[1]:
                    if len(descriptor) != 128: continue
                    encodings.append(descriptor)
                    person_id.append(personId[0])

            except TypeError:
                pass
        self.encodings, self.person_id = encodings, person_id
        return encodings, person_id

    def __get_descriptors_for_web_users(self):
        '''
        Получить encodings, person_id для обучения
        :return: encodings, person_id
        '''

        encodings = []
        person_id = []

        listUsers = app.config['components_obj'].BD.get_all_personId_for_web()

        for personId in listUsers:
            descriptors = app.config['components_obj'].BD.get_descriptors_by_personId_web(personId[0])[0]
            print(descriptors)
            try:
                for descriptor in descriptors[1]:
                    if len(descriptor) != 128: continue
                    encodings.append(descriptor)
                    person_id.append(personId[0])

            except TypeError:
                pass

        self.encodings, self.person_id = encodings, person_id
        return encodings, person_id


    def update_classification(self, mode):
        '''
        Сигнал на создание классификатора
        :mode: Обрабатывать для кого
        :return:
        '''
        #self.mode = {'web_user': [0, False], 'studets': [1, False]}
        print("Режим поменян", mode)
        self.mode[mode][1] = True
        self.status_trening = True

    def get_current_version(self, mode):
        '''
        Получает текущию версию
        :param mode: 0 - web 1 - students
        :return: id_dersion
        '''
        version = app.config['components_obj'].BD.get_latest_version(mode)
        #(2, 'тест для Web_2', 'classificator_web/1', datetime.datetime(2020, 4, 21, 8, 39, 16), '37146df1-756b-4919-965b-49b581e29592')

        return version[0]

    def close(self):
        self.status_threading = False

    def __del__(self):
        self.status_threading = False

    def run(self):
        '''

        :return:
        '''
        while self.status_threading:
            #Проверяем если время последнего обновления было довно или отправили сигнал на обучения то обучаем
            delta_time = datetime.datetime.now() - app.config['time_last_updates_classification']
            if self.status_trening or delta_time >= app.config['time_between_updates_classification']:
                print("Проверка для кого обучать")
                # Проверка для кого обучать
                if self.mode['web_user'][1]:
                    #обучаем для web пользователей
                    # формируем данные для обучения
                    print("обучаем для web пользователей")
                    print("формируем данные для обучения")
                    self.__get_descriptors_for_web_users()
                    # Обучаем
                    print("Обучаем")
                    print("clf_svm")
                    clf_svm = self.__train_cvm()
                    print("clf_knn")
                    clf_knn = self.__train_knn()
                    # Сохраняем и отправляем в базу
                    print("Сохраняем и отправляем в базу")
                    old_version = self.get_current_version(0)
                    now_version = int(old_version) + 1
                    changes = "По теребованию"
                    uuid_now = app.config['components_obj'].BD.get_now_uuid()
                    path_classification = os.path.join('data', 'classificator_web', str(uuid_now))

                    pathSave = os.path.join(app.config['path_dir_calassificator'], 'classificator_web', str(uuid_now))
                    os.mkdir(pathSave)
                    self.__save_model(clf_svm, os.path.join(pathSave, 'cvm_model.pk'))
                    self.__save_model(clf_knn, os.path.join(pathSave, 'knn_model.pk'))

                    #version_classification, changes, path_classification, data_time, uuid, mode
                    app.config['components_obj'].BD.pull_now_version(now_version, changes, path_classification, datetime.datetime.now(), uuid_now, 0)

                if self.mode['studets'][1]:
                    #Обучаем для студентов
                    # формируем данные для обучения
                    # Обучаем
                    # Сохраняем

                    pass

                #Выставляем параметры обратно
                self.mode['web_user'][1] = False
                self.mode['studets'][1] = False
                self.status_trening = False
                app.config['time_last_updates_classification'] = datetime.datetime.now()
