from flask import Flask
from flask_restful import Api
import queue
import datetime

app = Flask(__name__, static_url_path='/static')

#Добовляем ApI

from app_server.moduls.API.api import API_face_id

api = Api(app)
api.add_resource(API_face_id, "/api", "/api/<command>")
app.config['PORT_server_pull_data'] = 9000

DEBUG = False

#Settings parsec
app.config['url_parsec'] = "http://82.179.15.125:10101/IntegrationService/IntegrationService.asmx"
app.config['domain_parsec'] = '\xd0\x9a\xd0\xb5\xd0\xbc\xd0\x93\xd0\xa3'
app.config['user_parsec'] = 'test'
app.config['password_parsec'] = '123456'

#settings server
# app.config['IP_Server'] = '82.179.4.246'
# app.config['IP_Server'] = '192.168.1.69'
app.config['IP_Server'] = '192.168.1.104'
app.config['PORT_server'] = 2561
app.config['path_dir_temp'] = r'/home/dima/PycharmProjects/fase_idTest/app_server/data/temp'

#settings for data base
app.config['IP_DB'] = '127.0.0.1'
app.config['PORT_DB'] = 5432
app.config['login_DB'] = 'dima'
app.config['password_DB'] = 'asm123'
app.config['name_dataBase'] = 'faceid'
app.config['path_photo'] = r'/media/dima/d/PhotoBD'  #Путь до локальных пользователей

app.config['turnstiles'] = {}
app.config['turnstiles']['1'] = {'territoryId': 'c94830ab-2c17-4230-9561-4717cd98e207', 'comand': '1', 'info': "2 корпус 1 турникет вход"}
app.config['turnstiles']['2'] = {'territoryId': 'c94830ab-2c17-4230-9561-4717cd98e207', 'comand': '2', 'info': "2 корпус 1 турникет выход"}

app.config['time_between_updates_classification'] = datetime.timedelta(minutes=1, seconds=30)  #Время между созданием нового классификатора
app.config['time_last_updates_classification'] = datetime.datetime.now()  #Время последнего обновления классификатора

# from app_server.moduls.init_componects import init_components

from app_server.moduls import init_componects

from app_server.moduls.processing_faceId import processing_faceid


app.config['path_dir_calassificator'] = r'/home/dima/PycharmProjects/fase_idTest/app_server/data'


#Инициализируюм компоненты
app.config['components_obj'] = init_componects.init_components()


#Потоки для обработки
app.config['dict_check'] = {}
app.config['dict_res'] = {}

app.config['queue'] = queue.Queue()

app.config['processing_faceid_threading'] = []
for count in range(5):

    threading = processing_faceid(app.config['queue'], app.config['components_obj'], app.config['dict_check'], app.config['dict_res'])
    threading.name = "processing_faceid {}".format(str(count))
    app.config['processing_faceid_threading'].append(threading)
    threading.start()

from app_server import routes



