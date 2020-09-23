
import numpy as np
import glob
import matplotlib.pyplot as plt
from PIL import Image
import cv2

face_detector = cv2.CascadeClassifier(r'C:\Users\admin\PycharmProjects\FaseID_Keras\haarcascade_frontalface_default.xml')

def get_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # #
    # cv2.imshow("sds", image)
    # cv2.waitKey()

    return faces

def convert_PIL_TO_cv2(image_pil):
    pil_image = image_pil.convert('RGB')
    open_cv_image = np.array(pil_image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image

def read_csv_file(path_dep_csv):
    mat = np.zeros((480, 640), dtype='float32')
    i = 0
    j = 0

    with open(path_dep_csv) as file:
        for line in file:
            vals = line.split(',')
            for val in vals:
                if val == "\n": continue
                if float(val) > 1 or float(val) == 0: val = 0

                mat[i][j] = float(val)
                j += 1
                j = j % 640

            i += 1
        mat = np.asarray(mat)
    return mat

def create_wrong_rgbd(path_dep_csv, path_color, path_dep):
    mat_dep = read_csv_file(path_dep_csv)
    img = Image.open(path_color)
    img = np.asarray(img)

    x, y, w, h = get_face(img)[0]

    img = img#[y:y+h, x:x+w]
    image_dep = mat_dep#[y:y+h, x:x+w]


    full1 = np.zeros((h, w, 4))
    full1[:, :, :3] = img[:, :, :3]
    full1[:, :, 3] = mat_dep

    plt.imshow(img)
    plt.show()
    plt.imshow(image_dep)
    plt.show()


    #return np.array(full1)


id = '2'
import os
path_dep =     r'C:\Users\admin\PycharmProjects\FaseID_Keras\b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49\test\/' + id + '.png'
path_dep_csv = r'C:\Users\admin\PycharmProjects\FaseID_Keras\b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49\test\/' + id + '.csv'
path_color =   r'C:\Users\admin\PycharmProjects\FaseID_Keras\b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49\test\/' + id + '.png'


# path_photo_rgb = r'C:\Users\admin\PycharmProjects\FaseID_Keras\1d657214-3473-4d3e-981c-403266f485a2\photo_RGB'
# path_dep_csv = r'C:\Users\admin\PycharmProjects\FaseID_Keras\1d657214-3473-4d3e-981c-403266f485a2\photo_CSV'
# for i in os.listdir(path_dep_csv):
#     path_csv = os.path.join(path_dep_csv, i)

image = create_wrong_rgbd(path_dep_csv, path_color, path_dep)
print("размерность", image.shape)
print("пиксель центральный", image[240, 620])