## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2017 Intel Corporation. All Rights Reserved.

#####################################################
##              Align Depth to Color               ##
#####################################################

# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2

face_detector = cv2.CascadeClassifier(r'/home/dima/PycharmProjects/fase_idTest/expiriments/haarcascade_frontalface_default.xml')

def get_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # #
    # cv2.imshow("sds", image)
    # cv2.waitKey()

    return faces

# Create a pipeline
pipeline = rs.pipeline()

#Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Получение шкалы глубины датчика глубины (см. Пример с rs-align)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# Мы будем удалять фон объектов больше, чем
# clipping_distance_in_meters метров
clipping_distance_in_meters = 1 #1 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Создать объект выравнивания
# rs.align позволяет выполнять выравнивание кадров глубины по другим кадрам.
# «Align_to» - это тип потока, по которому мы планируем выравнивать кадры глубины.
align_to = rs.stream.color
align = rs.align(align_to)

# Streaming loop
try:
    while True:
        # Получить набор цветов и глубины
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Получить выровненные кадры
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Проверить, что оба кадра действительны
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        try:
            x, y, w, h = get_face(color_image)[0]
            print(x, y, w, h)
        except BaseException:
            continue

        color_image = color_image[y:y+h, x:x+w]
        depth_image = depth_image[y:y+h, x:x+w]

        # full1 = np.zeros((480, 640, 4))
        # full1[:, :, :3] = color_image[:, :, :3]
        # full1[:, :, 3] = depth_image
        #
        # print("full1", full1.shape)
        # print("depth_image", depth_image.shape)
        # print("color_image", color_image.shape)

        # cv2.imshow("full", full1)
        cv2.imshow("depth_image", depth_image)
        cv2.imshow("color_image", color_image)



        # # Удалить фон - установите пиксели дальше, чем clipping_distance, на серый
        # grey_color = 153
        # depth_image_3d = np.dstack((depth_image, depth_image, depth_image)) #depth image is 1 channel, color is 3 channels
        # bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        #
        # # Рендеринг изображений
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # images = np.hstack((bg_removed, depth_colormap))
        #
        #
        #
        # cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
        # cv2.imshow('Align Example', images)
        #
        # cv2.imshow('dep', color_image)
        # cv2.imshow('color', depth_image)
        #
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
finally:
    pipeline.stop()