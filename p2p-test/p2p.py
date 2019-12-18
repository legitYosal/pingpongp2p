import socket
import sys
import threading
import time

def sendxy(c):
    while True:
        for i in range(100):
            time.sleep(1)
            c.send(f'{i},{i * i}'.encode())

def recvxy(client):
    while True:
        print(client.recv(1024).decode())


def createconns():
    server = socket.socket()
    client = socket.socket()
    ihost = sys.argv[1]
    iport = int(sys.argv[2])
    shost = sys.argv[3]
    sport = int(sys.argv[4])
    server.bind((ihost, iport))
    print('trying to connect to host')
    try:
        client.connect((shost, sport))
        print('connected')
        server.listen(5)
        c, addr = server.accept()
        print(f'accept connection from{addr}')
        print('*****first connection then listened')
        try:
            send = threading.Thread(target=sendxy, args=(c, ))
            send.start()
            recv = threading.Thread(target=recvxy, args=(client, ))
            recv.start()
            # send.join()
            # recv.join()
        except Exception as e:
            print(str(e))
            print('threading error')
    except Exception as e:
        print(str(e))
        try:
            print('*********** connection failed starting server')
            server.listen(5)
            c, addr = server.accept()
            print(f'accept conn from{addr}')
            client.connect((shost, sport))
            print('********* first server then connection')
            try:
                send = threading.Thread(target=sendxy, args=(c, ))
                send.start()
                recv = threading.Thread(target=recvxy, args=(client, ))
                recv.start()
                # send.join()
                # recv.join()
            except Exception as e:
                print(str(e))
                print('threading error')
        except Exception as e:
            print(str(e))
            print('some wierd shit happend')
    client.close()
    server.close()


if len(sys.argv) < 5:
    raise Exception('what the heck need more ports')
createconns()
