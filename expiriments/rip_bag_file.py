'''Модуль предназначен для раскадровки видео
получим в итоге фотографии цветные
csv - с шлубинами
фотографии глубины'''

import cv2
import os
import pyrealsense2 as rs
import numpy as np
import argparse
import subprocess

def clear_dir(path_dir):
    '''
    Удаляет старые данные в папке если они есть если нет создает папку
    :param path_dir:
    :return:
    '''
    if os.path.exists(path_dir):
        if len(os.listdir(path_dir)) != 0:
            for name in os.listdir(path_dir):
                path_del = os.path.join(path_dir, name)
                print("file for del", path_del)
                os.remove(path_del)
    else:
        print("dir is non")
        os.mkdir(path_dir)

def rip_bag(path_people_bag, path_save_photo_RGB, path_save_photo_depth, path_save_photo_CSV):
    '''

    :param path_people_bag:
    :param path_save_photo_RGB:
    :param path_save_photo_depth:
    :param path_save_photo_CSV:
    :return:
    '''
    #rs-convert -i /media/dima/d/PhotoBD/b589bd6b-368c-4a81-92ae-547e40f73e06/3D/photo.bag -p /media/dima/d/PhotoBD/b589bd6b-368c-4a81-92ae-547e40f73e06/photo_RGB/photo -c
    commanda = 'rs-convert -i {} -p {} -c'.format(path_people_bag, os.path.join(path_save_photo_RGB, 'photo'))
    print(commanda)
    p = subprocess.Popen(commanda, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read()
    print(out)

def clear_photo(path_save_photo_RGB):
    '''
    Необходимо сделать что бы фотографий стало меньше
    :param path_save_photo_RGB:
    :return:
    '''
    threshold = 50

    listPhoto = os.listdir(path_save_photo_RGB)
    step = len(listPhoto) // threshold
    if step == 0: step = 1

    print("Шаг удаления:", step)

    print("итог фото:", len(range(0, len(listPhoto), step)))
    print("Количество фото", len(listPhoto))

    for i in range(0, len(listPhoto)):
        pathDel = os.path.join(path_save_photo_RGB, listPhoto[i])

        if i in range(0, len(listPhoto), step):
            print("i=",i,"ok")
            continue

        print(pathDel)
        #os.remove(pathDel)

    return len(range(0, len(listPhoto), step))



def main(path_dir_bd):

    list_people = os.listdir(path_dir_bd)
    count_photo = 0
    for count_id, key in enumerate(list_people):

        path_people_bag = os.path.join(path_dir_bd, key, r'3D', 'photo.bag')

        path_save_photo_RGB = os.path.join(path_dir_bd, key, r'photo_RGB')
        path_save_photo_depth = os.path.join(path_dir_bd, key, r'photo_depth')
        path_save_photo_CSV = os.path.join(path_dir_bd, key, r'photo_CSV')

        if not os.path.exists(path_people_bag):
            print("Файла не найдена")
            continue

        #Чистим данные
        # clear_dir(path_save_photo_RGB)
        # clear_dir(path_save_photo_depth)
        # clear_dir(path_save_photo_CSV)


        print("*"*20)
        print("Id", count_id)
        #print("Папка видео:", path_people_bag)
        print("Папка раскадровки:", path_save_photo_RGB)
        #print("Папка раскадровки:", path_save_photo_depth)
        #print("Папка раскадровки:", path_save_photo_CSV)

        #rip_bag(path_people_bag, path_save_photo_RGB, path_save_photo_depth, path_save_photo_CSV)


        count_photo = count_photo + clear_photo(path_save_photo_RGB)

    print("sdasd",count_photo)

if __name__ == '__main__':
    path_dir_bd = r'/media/dima/d/PhotoBD'
    main(path_dir_bd)