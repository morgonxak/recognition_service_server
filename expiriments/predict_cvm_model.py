'''
Данный модуль предназначен для проверки существующиф моделли нейронной сети по данным из bag Файла

'''

import face_recognition
from sklearn import svm
import os
import pickle
import cv2
import time
import pyrealsense2 as rs
import numpy as np
import logging

# add filemode="w" to overwrite
logging.basicConfig(filename="data_log.log", level=logging.INFO)

def predict_frame(frame, clf, key):
    # Найдите все лица на тестовом изображении, используя модель на основе HOG по умолчанию
    face_locations = face_recognition.face_locations(frame)
    no = len(face_locations)


    # Прогнозирование всех граней на тестовом изображении с использованием обученного классификатора

    oldTime = time.time()
    test_image_enc = face_recognition.face_encodings(frame)[0]
    name = clf.predict([test_image_enc])
    logging.info("Количество лиц: {}".format(no))
    logging.info(str(time.time() - oldTime))

    if len(name) != 0:
        if name[0] == key:
            logging.info("++++Пользователи   совподают +++++")
        else:
            logging.info("----Пользователи Не совподают ----")
            logging.info(name)




def rip_bag(path_people_bag, clf, key):

    if not os.path.exists(path_people_bag):
        print("Файла не найдена")
        return 0


    try:
        pipeline = rs.pipeline()

        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

        config.enable_device_from_file(path_people_bag, repeat_playback=False)

        profile = pipeline.start(config)

        playback = profile.get_device().as_playback()
        playback.set_real_time(False)

        i = 0
        while True:
            try:
                frames = pipeline.wait_for_frames()
                playback.pause()

            except RuntimeError as e:
                print("error, ", str(e))
                # pipeline.stop()

                print("Файл закрылся")
                #del pipeline
                print("del pipeline")
                # config = None
                print("del config")
                # del frames
                print("del frames")

                print("Переменные удалены")
                break
            else:
                i += 1
                color_frame = frames.get_color_frame()

                if i % 10 == 0:
                    print("predict_frame")
                    color_frame = np.asanyarray(color_frame.get_data())
                    img = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)
                    predict_frame(img, clf, key)


                if i >= 200:
                    break
                playback.resume()

    except BaseException as e:
        print("Errorrrrr", str(e))

def main(path_dir_bd, clf):

    list_people = os.listdir(path_dir_bd)

    for count_id, key in enumerate(list_people):

        path_people_bag = os.path.join(path_dir_bd, key, r'3D', 'photo.bag')
        path_save_photo = os.path.join(path_dir_bd, key, r'photo_2')

        if not os.path.exists(path_people_bag):
            print("Файла не найдена")
            continue

        print("Осталовь: ", len(list_people) - count_id)
        logging.info("*"*30)
        logging.info("Id {}".format(count_id))
        logging.info("Папка видео: {}".format(path_people_bag))
        logging.info("Папка раскадровки: {}".format(path_save_photo))

        rip_bag(path_people_bag, clf, key)
        logging.info("!" * 30)


if __name__ == '__main__':

    pathBD = r'/media/dima/d/PhotoBD'
    pathModel = r'/home/dima/PycharmProjects/fase_idTest/expiriments/cvm_model_v1.pk'
    clf = pickle.load(open(pathModel, 'rb'))
    main(pathBD, clf)