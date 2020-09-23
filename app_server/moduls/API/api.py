
from flask_restful import Api, Resource, reqparse
from flask import request

from app_server import app
from app_server.moduls.API import functional

import os


class API_face_id(Resource):
    '''
        api faceId
        Функционал:
        get
         -Получить количество пользователей (getNumberUsers)
         -Получить информацию о пользователе по его id (getUserInformationByUserId)
         -Получить информацию о пользователе по его ФИО (getInformationAboutTheUserByHisName)  --------------------
         -Получить версию последнего классификатора (getTheVersionOfTheLastClassifier)
         -Получить классификатор (getClassifier)

        Post
         -Создать пользователя с уникальным id (createUserWithUniqueId)
         -Создание нового пропукново пункта (createNewCheckpoint)  ---------

        delete
         -Удаление пользователя по ID (deleteUserById)
         -Удаление пропускново пункта (deleteCheckpoint) --------------

        put
         -Изменить информацию о пользователе по его ID (changeUserInformationByUserId)
         -Изменить параметры пропускново пункта (changeCheckpointSettings)  ------------
    '''


    def get(self, command='None'):

        if command == 'None':
            return self.__doc__, 200

        elif command == "getNumberUsers":
            count_users = app.config['components_obj'].BD.get_number_of_users()
            return str(count_users), 200

        elif command == "getUserInformationByUserId":
            parser = reqparse.RequestParser()
            parser.add_argument("person_id")
            params = parser.parse_args()
            if params['person_id'] == None:
                return self.__doc__, 200
            else:
                info_user = app.config['components_obj'].BD.getData_by_person_id(params['person_id'])
                if len(info_user) != 0:
                    return {'card_id_code': info_user[0][0],
                            'person_id': info_user[0][1],
                            'full_name': info_user[0][2]
                            }, 200

        elif command == "getInformationAboutTheUserByHisName":
            return "getInformationAboutTheUserByHisName"

        elif command == "getTheVersionOfTheLastClassifier":
            version = app.config['components_obj'].BD.get_latest_version()

            return {'version': version[0],
                    'changes': version[1]
                    }

        elif command == "getClassifier":
            #Получаем последнюю версию
            version = app.config['components_obj'].BD.get_latest_version()
            print(version)
            ipClien = request.remote_addr  #получаем IP клиента
            print("ipClien", ipClien)
            pathFile_classification = os.path.join(app.config['path_dir_calassificator'], version[2])  #Получаем путь до файлов котрые необходимо отправить

            response_create_zip = functional.create_zip_file(pathFile_classification, str(version[0]))  # создаем zip

            #отправляем
            res = app.config['components_obj'].server_pull_data.pullData(ipClien, response_create_zip)

            return {'version': version[0],
                    'changes': version[1],
                    'state': res
                    }

    def post(self, command='None'):
        '''

        :param command:
        :return:
        '''
        if command == 'None':
            return self.__doc__, 200

        elif command == "createUserWithUniqueId":
            parser = reqparse.RequestParser()
            parser.add_argument("card_id_code")
            parser.add_argument("person_id")
            parser.add_argument("full_name")
            parser.add_argument("photo_basa64")
            parser.add_argument("list_descriptor")
            params = parser.parse_args()

            info_user = app.config['components_obj'].BD.getData_by_person_id(params['person_id'])
            print(info_user)
            if len(info_user) != 0:
                #пользователь существует
                return "user_exists"
            else:
                print(len(info_user))
                if params['person_id'] == None or params['photo_basa64'] == None or params['list_descriptor'] == None:
                    return self.__doc__, 200
                else:
                                                                        #card_id_code, person_id, full_name, photo_rgb_base64, descriptor

                    response = app.config['components_obj'].BD.pushData(params['card_id_code'], params['person_id'], params['full_name'], params['photo_basa64'], params['list_descriptor'])
                    return str(response), 200

        elif command == "createNewCheckpoint":
            return "createNewCheckpoint", 200

    def delete(self, command='None'):
        if command == 'None':
            return self.__doc__, 200

        elif command == "deleteUserById":
            parser = reqparse.RequestParser()
            parser.add_argument("person_id")
            params = parser.parse_args()
            if params['person_id'] == None:
                return self.__doc__, 200
            else:
                info_user = app.config['components_obj'].BD.getData_by_person_id(params['person_id'])
                if len(info_user) != 0:
                    status = app.config['components_obj'].BD.del_user(params['person_id'])

                    return {'card_id_code': info_user[0][0],
                            'person_id': info_user[0][1],
                            'full_name': info_user[0][2],
                            'status': status
                            }
                else:
                    return "no User"

    def put(self, command='None'):
        if command == 'None':
            return self.__doc__, 200

        elif command == 'changeUserInformationByUserId':
            parser = reqparse.RequestParser()
            parser.add_argument("card_id_code")
            parser.add_argument("person_id")
            parser.add_argument("full_name")
            parser.add_argument("photo_basa64")
            parser.add_argument("list_descriptor")
            params = parser.parse_args()

            info_user = app.config['components_obj'].BD.getData_by_person_id(params['person_id'])
            if len(info_user) != 0:
                if params['person_id'] == None:
                    return self.__doc__, 200
                else:
                    # card_id_code, person_id, full_name, photo_rgb_base64, descriptor
                    response = app.config['components_obj'].BD.pushData(params['card_id_code'], params['person_id'],
                                                                        params['full_name'], params['photo_basa64'],
                                                                        params['list_descriptor'])
                    return str(response), 200
            else:
                return "no_user"




if __name__ == '__main__':
    '''Проверка Класса'''
    from flask import Flask
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(API_face_id, "/api", "/api/<command>")
    app.run(debug=True, port=123)
