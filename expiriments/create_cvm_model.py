# Train multiple images per person
# Find and recognize faces in an image using a SVC with scikit-learn

"""
Structure:
        <test_image>.jpg
        <train_dir>/
            <person_1>/
                <person_1_face-1>.jpg
                <person_1_face-2>.jpg
                .
                .
                <person_1_face-n>.jpg
           <person_2>/
                <person_2_face-1>.jpg
                <person_2_face-2>.jpg
                .
                .
                <person_2_face-n>.jpg
            .
            .
            <person_n>/
                <person_n_face-1>.jpg
                <person_n_face-2>.jpg
                .
                .
                <person_n_face-n>.jpg
"""

import face_recognition
from sklearn import svm
import os
import pickle
import time

# Training the SVC classifier

# The training data would be all the face encodings from all the known images and the labels are their names
encodings = []
names = []

# Training directory
path_BD = r'/media/dima/d/PhotoBD'

train_dir = os.listdir(path_BD)
print("В тренировке учавствуют количество людей:", len(train_dir))

old_time_load_data = time.time()

# Loop through each person in the training directory
for count_key, person in enumerate(train_dir):
    path_person = os.path.join(path_BD, person, 'photo_2')
    pix = os.listdir(path_person)
    print("Начало загрузки фотографий для:", person)
    print("Номерн пользователя:", count_key)
    print("Количество фотографий:", len(pix))
    print("Путь до фотографий:", path_person)

    for person_img in pix:

        path_person_image = os.path.join(path_person, person_img)

        face = face_recognition.load_image_file(path_person_image)
        face_bounding_boxes = face_recognition.face_locations(face)

        #Если тренировочный образ содержит ровно одно лицо
        if len(face_bounding_boxes) == 1:
            face_enc = face_recognition.face_encodings(face)[0]
            # Добавить кодировку лица для текущего изображения с соответствующей меткой (именем) к данным тренировки
            encodings.append(face_enc)
            names.append(person)
        else:
            print(person + "/" + person_img + " was skipped and can't be used for training")

print("Загрузка данных завершена")
old_time_load_data = time.time() - old_time_load_data
old_time_fit = time.time()

# Create and train the SVC classifier
clf = svm.SVC(gamma='scale')
clf.fit(encodings, names)

old_time_fit = time.time() - old_time_fit

print("Модуль обучена")
print("Время обучения:")
print("Загрузка данных:", old_time_load_data)
print("Обучения:", old_time_fit)

filename = '/home/dima/PycharmProjects/fase_idTest/expiriments/finalized_model.sav'
pickle.dump(clf, open(filename, 'wb'))

print("Запись сети в файл завершена")


# Load the test image with unknown faces into a numpy array
test_image = face_recognition.load_image_file(r'/home/dima/Документы/alena.jpg')

# Найдите все лица на тестовом изображении, используя модель на основе HOG по умолчанию
face_locations = face_recognition.face_locations(test_image)
no = len(face_locations)
print("Number of faces detected: ", no)

# Прогнозирование всех граней на тестовом изображении с использованием обученного классификатора
print("Found:")
for i in range(no):
    test_image_enc = face_recognition.face_encodings(test_image)[i]
    name = clf.predict([test_image_enc])
    print(*name)