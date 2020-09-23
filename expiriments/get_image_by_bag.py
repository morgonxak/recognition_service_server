'''
Предназначен для раскадровки Bag ФАйла
Посути бесполезный модель так так есть встроиная программа rs_converteg  в RealSens SDK
'''


import cv2
import os
import pyrealsense2 as rs
import numpy as np
import argparse


def clear_dir(path_dir):
    '''

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


def rip_bag(path_people_bag, path_save_photo):

    if not os.path.exists(path_people_bag):
        print("Файла не найдена")
        return 0
    clear_dir(path_save_photo)

    try:
        pipeline = rs.pipeline()

        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

        config.enable_device_from_file(path_people_bag, repeat_playback=False)

        profile = pipeline.start(config)

        playback = profile.get_device().as_playback()
        playback.set_real_time(False)
        colorizer = rs.colorizer()

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

                depth_frame = frames.get_depth_frame()


                print("Saving frame:", i)
                color_frame = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                img = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)

                f = open(os.path.join(path_save_photo, str(i) + '.csv'), 'w')

                for y in range(480):
                    for x in range(640):
                        dist = depth_frame.get_distance(x, y)
                        f.write(str(dist))
                        f.write(',')
                    f.write('\n')
                f.close()

                cv2.imwrite(os.path.join(path_save_photo, str(i) + '.png'), img)
                cv2.imwrite(os.path.join(path_save_photo, str(i) + '_dep.png'), depth_image)

                if i >= 50:
                    break
                playback.resume()

    except BaseException as e:
        print("Errorrrrr", str(e))



def main(path_dir_bd):

    list_people = os.listdir(path_dir_bd)

    for count_id, key in enumerate(list_people):

        path_people_bag = os.path.join(path_dir_bd, key, r'3D', 'photo.bag')
        path_save_photo = os.path.join(path_dir_bd, key, r'photo_2')

        if not os.path.exists(path_people_bag):
            print("Файла не найдена")
            continue
        clear_dir(path_save_photo)

        print("*"*20)
        print("Id", count_id)
        print("Папка видео:", path_people_bag)
        print("Папка раскадровки:", path_save_photo)

        rip_bag(path_people_bag, path_save_photo)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # parser.add_argument("-b", "--path_people_bag", type=str, help="Bag file to read")
    # parser.add_argument("-s", "--path_save_photo", type=str, help="Bag file to read")
    # args = parser.parse_args()

    # path_dir_bd = r'/media/dima/d/PhotoBD'

    #rip_bag(args.path_people_bag, args.path_save_photo)
    #python3 /home/dima/PycharmProjects/fase_idTest/expiriments/get_image_by_bag.py -b /media/dima/d/PhotoBD/56196ac9-a266-4f75-89ff-afcef8eb61ca/3D/photo.bag -s /media/dima/d/PhotoBD/56196ac9-a266-4f75-89ff-afcef8eb61ca/photo_2


    # main(path_dir_bd)

    #b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49
    path_people_bag = r'/media/dima/d/PhotoBD/b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49/3D/photo.bag'
    path_save_photo = r'/media/dima/d/PhotoBD/b9e1d2bc-ac4f-4b5b-bec3-fd586c8c3e49/test'

    rip_bag(path_people_bag, path_save_photo)