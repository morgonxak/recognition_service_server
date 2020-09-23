# Recognition servis server [23.09.2020]
Распознование по RGB лицу. Состоит из двух частей: 
1. _Recognition servis server_ - Содержит в себе систему для идентификации пользователей, создание классификатора и пользовательский интерфейс для взаимодействия с базой данных
2. _Recognition servis client_ - Raspberry pi способная находить пользователей на фотографии создавать из дискриптор и отправлять на сервер для подтверждения аунтификации.

## Основные пакеты:
0. apt install cmake
0. apt install python3.7-dev

## Установка:
0. Создать виртуальное окружения python3 -m venv door, активировать source door/bin/activate
0. pip install -r requirements.txt
0. Запуск: pyhton run_web.py

## Описание папок проекта
expirements - Тестовые файлы.

rs - ресурсы проекта (содержат обученные модели и классификатор для поискаа лиц).

## Схема взаимодействия модулей

![alt text](https://github.com/morgonxak/door/blob/master/rs/scheme.png)


## REST-API:
api faceId
Функционал:
### get
0. Получить количество пользователей (getNumberUsers)
0. Получить информацию о пользователе по его id (getUserInformationByUserId)
0. Получить информацию о пользователе по его ФИО (getInformationAboutTheUserByHisName)  Не реализованно
0. Получить версию последнего классификатора (getTheVersionOfTheLastClassifier)
0. Получить классификатор (getClassifier)

### Post
0. Создать пользователя с уникальным id (createUserWithUniqueId)
0. Создание нового пропукново пункта (createNewCheckpoint)  Не реализованно

### delete
0. Удаление пользователя по ID (deleteUserById)
0. Удаление пропускново пункта (deleteCheckpoint) Не реализованно

### put
0. Изменить информацию о пользователе по его ID (changeUserInformationByUserId)
0. Изменить параметры пропускново пункта (changeCheckpointSettings)  Не реализованно

## Что хочется сделать
1. Добавить логирование
2. Добавить авто обновления базы классификаторов

  

