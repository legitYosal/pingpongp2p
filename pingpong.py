import arcade
import os
import socket
import sys
import time
import threading

WIDTH = 600
HEIGHT = 600
TITLE = "ping pong"
SPEED = 5
BALLSPEED = 2
class Rocket(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
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
        self.pong    = None
        self.dottedLine = None
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
        self.pong.change_x = BALLSPEED
        self.pong.change_y = BALLSPEED
        try:
            threading.Thread(target=self.createconns())
        except Exception as e:
            print('************************')
            print(str(e))

    def on_draw(self):
        arcade.start_render()
        self.playerR.draw()
        self.playerL.draw()
        self.dottedLine.draw()
        self.pong.draw()
        arcade.draw_text(f"{self.scoreL}              {self.scoreR}",
                         WIDTH/2 - 75, HEIGHT - 30, arcade.color.WHITE, 28)


    def on_update(self, delta_time):
        self.playerR.update()
        self.playerL.update()
        self.pong.update()

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
            self.passed()
        elif self.pong.center_x > WIDTH - 1:
            self.scoreL += 1
            self.passed()

    def on_key_press(self, key, modifires):
        if key == arcade.key.UP:
            self.playerR.change_y = SPEED
        elif key == arcade.key.DOWN:
            self.playerR.change_y = -SPEED
        if key == arcade.key.W:
            self.playerL.change_y = SPEED
        elif key == arcade.key.S:
            self.playerL.change_y = -SPEED

    def on_key_release(self, key, modifires):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.playerR.change_y = 0
        if key == arcade.key.W or key == arcade.key.S:
            self.playerL.change_y = 0
    def sendxy(self, c, masterBall):
        while True:
            if masterBall:
                c.send(f'{self.playerL.center_y},{self.pong.center_x},{self.pong.center_y}'.encode())
            else:
                c.send(f'{self.playerR.center_y}'.encode())
            time.sleep(0.01)

    def recvxy(self, client, masterBall):
        while True:
            if masterBall:
                y = client.recv(1024).decode()
                self.playerR.center_y = int(float(y))
                print('recived :',y)
            else:
                y, ballx, bally = client.recv(1024).decode().split(',')
                self.pong.center_x = int(float(ballx))
                self.pong.center_y = int(float(bally))
                self.playerL.center_y = int(float(y))
                print('recived :',y,ballx, bally)

    def createconns(self):
        server = socket.socket()
        client = socket.socket()
        ihost = sys.argv[1]
        iport = int(sys.argv[2])
        shost = sys.argv[3]
        sport = int(sys.argv[4])
        server.bind((ihost, iport))
        print('trying to connect to host')
        masterBall = False
        try:
            client.connect((shost, sport))
            print('connected')
            server.listen(5)
            c, addr = server.accept()
            print(f'accept connection from{addr}')
            print('*****first connection then listened')
            masterBall = True
            try:
                send = threading.Thread(target=self.sendxy, args=(c, masterBall, ))
                send.start()
                recv = threading.Thread(target=self.recvxy, args=(client, masterBall, ))
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
                    send = threading.Thread(target=self.sendxy, args=(c, masterBall, ))
                    send.start()
                    recv = threading.Thread(target=self.recvxy, args=(client, masterBall, ))
                    recv.start()
                    # send.join()
                    # recv.join()
                except Exception as e:
                    print(str(e))
                    print('threading error')
            except Exception as e:
                print(str(e))
                print('some wierd shit happend')
        # client.close()
        # server.close()


def main():
    game = PingPong(WIDTH, HEIGHT, TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
