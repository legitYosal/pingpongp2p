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
class Rocket(arcade.Sprite):
    def update(self):
        self.center_y += self.change_y
        if self.center_y - 95 < 0:
            self.center_y = 95
        elif self.center_y + 95 > HEIGHT - 1:
            self.center_y = HEIGHT - 95
        # print("plyaerR x:", self.change_x, " y:", self.change_y)
class Ball(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.center_y < 5 or self.center_y > HEIGHT - 6:
            self.change_y = -self.change_y


class PingPong(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        self.playerR = None
        self.playerR = None
        self.scoreL  = 0
        self.scoreR  = 0
        self.change_y = 0
        self.last_change_y = 0
        self.where =    None
        self.server   = None
        self.pong    = None
        self.dottedLine = None
        self.masterBall = None
        arcade.set_background_color(arcade.color.BLACK)

    def passed(self):
        self.playerL.center_x = 10
        self.playerL.center_y = HEIGHT/2
        self.playerR.center_x = WIDTH - 10
        self.playerR.center_y = HEIGHT/2
        self.pong.center_x = 35
        self.pong.center_y = HEIGHT/2
        self.pong.change_x = BALLSPEED
        self.pong.change_y = BALLSPEED

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
        self.pong = Ball("static/ball.png", 0.7)
        self.pong.center_x = 35
        self.pong.center_y = HEIGHT/2
        start_new_thread(self.initconn, ())

    def on_draw(self):
        arcade.start_render()
        self.playerR.draw()
        self.playerL.draw()
        self.dottedLine.draw()
        self.pong.draw()
        arcade.draw_text(f"{self.scoreL}              {self.scoreR}",
                         WIDTH/2 - 75, HEIGHT - 30, arcade.color.WHITE, 28)


    def on_update(self, delta_time):
        self.playerL.update()
        self.pong.update()
        self.playerR.update()

    def update(self, delta_time):
        HitR = arcade.check_for_collision(self.pong, self.playerR)
        HitL = arcade.check_for_collision(self.pong, self.playerL)
        if HitR or HitL:
            self.pong.change_x = - self.pong.change_x
            if HitR:
                self.pong.center_x -= 5
            else:
                self.pong.center_x += 5
        if self.pong.center_x < 0:
            self.scoreR += 1
            time.sleep(0.1)
            self.passed()
        elif self.pong.center_x > WIDTH - 1:
            self.scoreL += 1
            time.sleep(0.1)
            self.passed()

    def on_key_press(self, key, modifires):
        if key == arcade.key.UP:
            self.change_y = SPEED
        elif key == arcade.key.DOWN:
            self.change_y = -SPEED

    def on_key_release(self, key, modifires):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.change_y = 0

    def listentoserver(self, server):
        data = None
        while True:
            time.sleep(0.002)
            data = server.recv(1024)
            if not data:
                print('** conn closed last data was: ', data)
                break
            data = data.decode('ascii')
            # test = data is 'start'
            print(f'from server: ({data})')
            if data == 'start':
                print('recevied start signal')
                self.pong.change_x = BALLSPEED
                self.pong.change_y = BALLSPEED
            elif data == 'stop':
                pass
            else:
                Ly, Ry = data.split(',')
                if self.where is 'R':
                    self.last_change_y = int(float(Ry))
                elif self.where is 'L':
                    self.last_change_y = int(float(Ly))
                else:
                    print('who was that?')
                self.playerR.change_y = int(float(Ry))
                self.playerL.change_y = int(float(Ly))

        server.close()

    def initconn(self):
        host = sys.argv[1]
        port = int(sys.argv[2])
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.connect((host,port))
        data = server.recv(1024)
        if not data:
            print('** connection was closed by server')
            client.close()
            return
        data = data.decode('ascii')
        print('where recv from server: ', data)
        self.where = data
        start_new_thread(self.listentoserver, (server,))
        while True:
            time.sleep(0.002)
            if self.last_change_y is not self.change_y:
                data = f'{self.change_y}'.encode('ascii')
                server.send(data)

        server.close()

def main():
    game = PingPong(WIDTH, HEIGHT, TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
