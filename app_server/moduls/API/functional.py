from app_server import app
import os
import socket
import zipfile

def create_zip_file(pathDir:str, name:str):

    pathSave_zip_file = os.path.join(app.config['path_dir_temp'], name+'.zip')
    if os.path.isfile(pathSave_zip_file):
        return pathSave_zip_file

    z = zipfile.ZipFile(pathSave_zip_file, 'w')  # Создание нового архива

    for file in os.listdir(pathDir):  # Список всех файлов и папок в директории folder
        print(os.path.join(pathDir, file))
        z.write(os.path.join(pathDir, file), file)  # Создание относительных путей и запись файлов в архив

    z.close()

    return pathSave_zip_file

if __name__ == '__main__':
    create_zip_file('/home/dima/PycharmProjects/fase_idTest/app_server/data/classificators/0', '0')

