# Recognition servis client [23.09.2020]
Распознование по RGB лицу. Состоит из двух частей: 
1. _Recognition servis server_ - Содержит в себе систему для идентификации пользователей, создание классификатора и пользовательский интерфейс для взаимодействия с базой данных
2. _Recognition servis client_ - Raspberry pi способная находить пользователей на фотографии создавать из дискриптор и отправлять на сервер для подтверждения аунтификации.

## Основные пакеты:
0. apt install cmake
0. apt install python3.7-dev


## Установка:
0. Создать виртуальное окружения python3 -m venv door, активировать source door/bin/activate
0. pip install -r requirements.txt
0. поменять путь до папки с проектом в файле app_face_recognition/__init__.py в переменной pathProject_book поменять путь на свой.
0. Запуск: pyhton run_web.py


## Описание папок проекта
expirements - Тестовые файлы.

rs - ресурсы проекта (содержат обученные модели и классификатор для поискаа лиц).

app_face_recognition - Основное приложения 
1. modul - Основные компоненты проекты
2. static - статика для Web страници
3. templates - Html файлы проекта основной файл index.html
4. routing.py - марруты сайта

## Схема взаимодействия модулей

![alt text](https://github.com/morgonxak/door/blob/master/rs/scheme.png)


## Что хочется сделать
1. Добавить логирование
2. Добавить авто обновления базы классификаторов

  

