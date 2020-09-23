'''
Модуль для проверки распознования миц и для дообучения CVM, Knn нейронных сетей
'''
import threading
import face_recognition
import cv2

class processing_faceid(threading.Thread):

    def __init__(self, queue, obj_init_db, dict_check, dict_res):
        '''
        Принимает:
            -стек
            -базу данных
            -словарь для результатов распознования
        :param queue:
        :param obj_init_db:
        '''
        super().__init__()

        self.queue = queue
        self.obj_init_db = obj_init_db
        self.dict_check = dict_check
        self.dict_res = dict_res

    def predict_cvm(self, face_encoding):
        '''
        Проверяет пользователя по модели CVM
        :param face_encoding: Получаем дескриптор
        :return: person_id -- Уникальный идентификатор пользователя
        '''

        # Прогнозирование всех граней на тестовом изображении с использованием обученного классификатора

        person_id = self.obj_init_db.model_cvm.predict([face_encoding])

        return person_id

    def predict_knn(self, face_encoding, tolerance=0.4):
        '''
        Проверяет пользователя по модели knn
        :param face_encoding:
        :param tolerance: Коэфициент похожести
        :return: person_id, dist == уникальный идентификатор и дистанция до него
        '''
        closest_distances = self.obj_init_db.model_knn.kneighbors([face_encoding], n_neighbors=1)

        are_matches = [closest_distances[0][i][0] <= tolerance for i in range(1)]

        if are_matches[0]:
            person_id = self.obj_init_db.model_knn.predict([face_encoding])[0]
        else:
            person_id = "Unknown"

        return person_id

    def accurate_check(self, personID_predict_cvm, personID_predict_knn):
        '''
        Проверка фотографии с полощью нескольких нейронных сетей
        :param personID_predict_cvm:
        :param personID_euclidean_distance:
        :return: personID или None
        '''
        if personID_predict_cvm == personID_predict_knn:
            return personID_predict_cvm[0]
        else:
            return "Unknown"


    def run(self):
        '''
        Фходные данные Изображения в формате RGB
        :return:
        '''
        while True:
            #Получаем задание
            frame, id_devices = self.queue.get()
            #print("Задание от ", id_devices)
            # Изменение размера кадра видео до 1/4 для более быстрой обработки распознавания лиц
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Найти все лица в текущем кадре видео
            face_locations = face_recognition.face_locations(small_frame)

            #Проверка если количество лиц на кадре больше 1 или нет лиц совсем
            if len(face_locations) != 1:
                print("Проверка если количество лиц на кадре больше 1 или нет лиц совсем")
                continue

            #Вычесляем дескриптор
            face_encoding = face_recognition.face_encodings(small_frame, face_locations)[0]

            personID_predict_cvm = self.predict_cvm(face_encoding)
            personID_predict_knn = self.predict_knn(face_encoding)


            #Проверка кадра несколькими способами распознания
            personID = self.accurate_check(personID_predict_cvm, personID_predict_knn)


            #################################  Проверка на сножественное совподения  ########################################

            if id_devices in self.dict_check:
                #ключ есть
                self.dict_check[id_devices].append(personID)
                set_dict_res = set(self.dict_check[id_devices])

                if len(self.dict_check[id_devices]) >= 1:
                    print("Количество обработанных фото:", len(self.dict_check[id_devices]))

                    if len(self.dict_check[id_devices]) == len(set_dict_res):
                        #Все пользователи одинаковые
                        print("Пользователи одинаковые")
                        self.dict_check[id_devices] = []
                        self.dict_check[id_devices].append(personID)  #Сомнительная операция

                        self.dict_res[id_devices] = personID
                    else:
                        #Есть не совподения
                        self.dict_check[id_devices] = []
            else:
                self.dict_check[id_devices] = []




