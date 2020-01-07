import arcade
import os
import socket
import sys
import time
import threading
from _thread import *

WIDTH = 600
HEIGHT = 600
TITLE = "ping pong"
SPEED = 5
BALLSPEED = 2
# print_lock = threading.Lock()

class Rocket(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.center_y - 95 < 0:
            self.center_y = 95
        elif self.center_y + 95 > HEIGHT - 1:
            self.center_y = HEIGHT - 95
        # print("plyaerR x:", self.change_x, " y:", self.change_y)

class PingPong(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        self.playerR = None
        self.playerR = None
        self.scoreL  = 0
        self.scoreR  = 0
        self.dottedLine = None
        self.clients = []
        arcade.set_background_color(arcade.color.BLACK)

    def passed(self):
        # if i recieve one lose signal
        pass

    def setup(self):
        self.scoreL  = 0
        self.scoreR  = 0
        self.dottedLine = arcade.Sprite("static/dottedLine.png", 0.5)
        self.dottedLine.center_x = WIDTH/2
        self.dottedLine.center_y = HEIGHT/2
        self.playerL = Rocket("static/pong.png", 0.6)
        self.playerL.center_x = 10
        self.playerL.center_y = HEIGHT/2
        self.playerR = Rocket("static/pong.png", 0.6)
        self.playerR.center_x = WIDTH - 10
        self.playerR.center_y = HEIGHT/2
        start_new_thread(self.createconns, ())

    def on_draw(self):
        arcade.start_render()
        self.playerR.draw()
        self.playerL.draw()
        self.dottedLine.draw()
        arcade.draw_text(f"{self.scoreL}              {self.scoreR}",
                         WIDTH/2 - 75, HEIGHT - 30, arcade.color.WHITE, 28)


    def on_update(self, delta_time):
        self.playerL.update()
        self.playerR.update()


    def update(self, delta_time):
        pass

    def clientHandler(self, client):
        where = None
        for pack in self.clients:
            if client in pack:
                where = pack[1]
        data = f'{where}'
        data = data.encode('ascii')
        client.send(data)
        time.sleep(0.1)
        if where is 'R':
            data = f'start'
            data = data.encode('ascii')
            print('sending start signal')
            for pack in self.clients:
                others = pack[0]
                others.send(data)
        while True:
            time.sleep(0.002)
            data = client.recv(1024)
            if not data:
                print('** closed connection by client')
                break
            data = data.decode('ascii')

            if where == 'R':
                print('             RR:',data)
                self.playerR.change_y = int(float(data))
                data = f'{self.playerL.change_y},{data}'
            elif where == 'L':
                print('LL:',data)
                self.playerL.change_y = int(float(data))
                data = f'{data},{self.playerR.change_y}'
            else:
                print('what the hell was that??????')
                break

            data = data.encode('ascii')
            for pack in self.clients:
                others = pack[0]
                others.send(data)
            # handle data to others
        client.close()

    def createconns(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shost = sys.argv[1]
        sport = int(sys.argv[2])
        server.bind((shost, sport))
        where = None
        print('** server binded to socket: ', server)
        server.listen(5)
        print('** server listening...')
        while True:
            client, addr = server.accept()
            # print_lock.acquire()
            print('** accepted conn from: ', addr)
            # start_new_thread(clientHandler, (client,))
            if len(self.clients) == 0:
                # first client
                self.clients.append((client, 'L'))
            elif len(self.clients) == 1:
                # secound client
                self.clients.append((client, 'R'))
            else:
                # get the fucck out of here we dont want you
                client.close()
            # ACK: send to client info of the game it has the info for now
            # raise thread for recieve and sending
            start_new_thread(self.clientHandler, (client,))
        server.close()


def main():
    game = PingPong(WIDTH, HEIGHT, TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
