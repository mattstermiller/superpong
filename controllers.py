from pygame.constants import *


class PlayerController():
    def __init__(self, paddle, upKey, downKey):
        self.paddle = paddle
        self.upKey = upKey
        self.downKey = downKey

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == self.upKey:
            self.paddle.up()
        elif event.type == KEYDOWN and event.key == self.downKey:
            self.paddle.down()
        elif event.type == KEYUP and (event.key in (self.upKey, self.downKey)):
            self.paddle.stop()
        else:
            return False
        return True


class AIController:
    def __init__(self, paddle):
        self.paddle = paddle

    def update(self):
        pass
