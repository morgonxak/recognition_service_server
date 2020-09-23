'''

'''

import os
import socket
import threading


class server_pull_data(threading.Thread):
    '''
    Класс для передачи данных с сервера клиенту
    '''
    def __init__(self, ip_server, port_server):
        '''

        :param ip_server:
        :param port_server:
        '''

        super().__init__()
        self.listConnect = {}

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((ip_server, port_server))
        self.sock.listen()

    def run(self) -> None:
        '''
        Отслеживаем новых пользователей
        :return:
        '''
        try:
            while True:
                conn, addr = self.sock.accept()
                self.listConnect[addr[0]] = conn
        except KeyboardInterrupt:
            self.sock.close()

    def pullData(self, ip, pathFile):
        '''
        Отправляем данные определеннуму пользователю
        :param ip:
        :param pathFile:
        :return:
        '''

        conn = self.listConnect.get(ip, None)

        if not conn is None:
            print("отправка")
            sf = conn.fileno()
            lf = os.open(pathFile, os.O_RDONLY)

            while os.sendfile(sf, lf, None, 1024 * 1024 * 10) > 0:
                print('.', end='')

            conn.close()
            del self.listConnect[ip]
            return 0
        else:
            return -1

    def __del__(self):
        self.sock.close()




import time
if __name__ == '__main__':
    path_file = r'/home/dima/PycharmProjects/fase_idTest/app_server/data/classificators/0/cvm_model.pk'
    ipUser = '127.0.0.1'

    testServer = server_pull_data('127.0.0.1', 9000)
    testServer.start()
    print("run")
    time.sleep(10)
    print("pull")
    testServer.pullData(ipUser, path_file)
    time.sleep(5)
    print(testServer.listConnect)
