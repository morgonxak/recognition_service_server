
from app_faceId import app
from flask import request, render_template, make_response

from PIL import Image
from io import BytesIO
import cv2
import base64
import numpy as np
import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from app_faceId.moduls.trening_models_cvm_knn import class_training

import json

@app.route('/')
@app.route('/index')
def index():
    count_users = app.config['components_obj'].BD.get_number_of_users()
    count_users_web = app.config['components_obj'].BD.get_number_of_users_web()
    return render_template("index.html", count_users=[count_users, count_users_web], URL=app.config['IP_Server'] + ':' + str(app.config['PORT_server'])) # "Количество пользователей в системе: {}".format(app.config['components_obj'].BD.get_number_of_users())

@app.route('/testSignalClassification')
def test_classification():
    app.config['components_obj'].thread_trening.update_classification('web_user')
    return 0

@app.route('/addUser', methods=['GET', 'POST'])
def add_user_web():
    '''
    Вызывает окно и добовляет фотографии позьзователя в систему
    :return:
    '''
    if request.method == 'POST':

        person_id = str(uuid.uuid4())

        last_name = request.form.get("last_name")
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        post = request.form.get("post")

        photoRGB = request.files.get("photoRGB")
        photos = request.files.getlist("photos")

        os.mkdir(os.path.join(app.config['path_dir_temp'], person_id))

        #Сохраняем фотографию пользователя
        filename = secure_filename(photoRGB.filename)
        path_photo_RGB = os.path.join(app.config['path_dir_temp'], person_id, "Photo" + filename[filename.rfind('.'):])
        photoRGB.save(path_photo_RGB)

        #Фото для тренировки сети

        for count, photo_trener in enumerate(photos):
            print(photo_trener)
            filename = secure_filename(photo_trener.filename)
            photo_trener.save(os.path.join(app.config['path_dir_temp'], person_id, str(count) + filename[filename.rfind('.'):]))


        #Заполняем базу и начинаем тренировку
        #person_id, last_name, first_name, middle_name, photo_rgb_base64, descriptor, post

        photo_rgb_base64 = app.config['components_obj'].BD.convert_image_base64(path_photo_RGB)

        pathPhoto_trener = os.path.join(app.config['path_dir_temp'], person_id)
        list_photo_trener = os.listdir(pathPhoto_trener)

        list_descriptor = []

        for photo in list_photo_trener:
            path_photo = os.path.join(pathPhoto_trener, photo)
            img = cv2.imread(path_photo)
            descriptor = class_training.image_to_descriptor(img)
            if descriptor is None:
              continue
            list_descriptor.append(descriptor.tolist())

        app.config['components_obj'].BD.pushData_by_web(person_id, last_name, first_name, middle_name, photo_rgb_base64, list_descriptor, post)

        return render_template('add_webUser.html', URL=app.config['IP_Server'] + ':' + str(app.config['PORT_server']))

    return render_template('add_webUser.html', URL=app.config['IP_Server'] + ':' + str(app.config['PORT_server']))


@app.route('/pull/<id_devices>', methods=['GET', 'POST'])
def receipt_ima
    ge_from_devices(id_devices):
    '''
    Принимает изображения с устройства
    :param id_devices:
    :return:
    '''
    if request.method == 'POST':
        req_data = request.get_data()
        try:
            im = Image.open(BytesIO(base64.b64decode(req_data[22:])))
        except BaseException as e:
            print("Error: " + str(e))
            return "Error: " + str(e)

        opencvImage = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)

        app.config['queue'].put([opencvImage, id_devices])


        return make_response("<h2>404 Error</h2>", 200)

    return render_template('recognition.html', URL=app.config['IP_Server'] + ':' + str(app.config['PORT_server']), id_devices=id_devices)


@app.route('/get_res/<id_devices>', methods=['GET', 'POST'])
def pull_res_from_devices(id_devices):
    '''
    Как появится результат отдает результат
    :param id_devices:
    :return:
    '''
    if id_devices in app.config['dict_res']:

        personID = app.config['dict_res'][id_devices]
        #my_dict.pop('key', None)
        app.config['dict_res'].pop(id_devices, None)
        print('dict_check', personID)

        if personID == 'Unknown':
            return "Unknown"
        else:
            #[('None', 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49', 'Шумелев Дмитрий Игоревич')]
            full_name = app.config['components_obj'].BD.getData_by_person_id(personID)[0][2]

            access_is_allowed(personID, id_devices)
            return str(full_name)
    else:
        return 'None'


##################  Дополнительный функционал

def access_is_allowed(personID, id_devices):
    '''
    пользователь распознан:
    записать события прохода
    открыть проход

    :param personID:
    :param id_devices:
    :return:
    '''
    #[('004EF89D', 'b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49', 'Шумелев Дмитрий Игоривич')]
    dict_data = {}
    dict_data['person_id'] = personID
    dict_data['time_event'] = str(datetime.datetime.now())
    dict_data['events'] = "Открытия двери"
    dict_data['event_source'] = "ТЕстовая дверь"
    dict_data['subject'] = "тест"
    dict_data['summary'] = "тест"

    app.config['components_obj'].BD.pull_event(dict_data)

