import os
import socket
import io
s = socket.socket()

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s = socket.socket()
s.connect(('127.0.0.1', 9000))

pp = open('test.img', 'wb')

buf = memoryview(bytearray(1024*1024*10))
nbytes = 1

while nbytes:
    toread = 1024*1024*10
    view = buf[:]
    while toread:
       nbytes = s.recv_into(view, toread)
       view = view[nbytes:]
       toread -= nbytes
       if nbytes == 0:
            buf=buf[:-toread]
            break

    pp.write(buf)
    print('.', end='')
