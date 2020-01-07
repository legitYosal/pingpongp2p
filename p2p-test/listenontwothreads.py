import socket
import threading
import sys
import time
def servr(name, wait):
    s = socket.socket()
    host = sys.argv[1]
    port = int(sys.argv[2])
    time.sleep(wait)
    s.bind((host, port))
    print(f'start listening.... with name: {name}')
    s.listen(5)
    c, addr = s.accept()
    print(f'{name} accepted from addr {addr}')
    time.sleep(3)
    s.close

def client():
    s = socket.socket()
    host = sys.argv[1]
    port = int(sys.argv[2])
    try:
        s.connect((host, port))
    except:
        print('connection refuesd')
    print('client attached')
    time.sleep(3)
    s.close()

a = threading.Thread(target=servr,args=('ONE',1, ))
b = threading.Thread(target=servr,args=('TWO',2, ))
a.start()
b.start()
c = threading.Thread(target=client)
c.start()

a.join()
b.join()
c.join()
