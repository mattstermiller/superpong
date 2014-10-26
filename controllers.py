from pygame.constants import *


class PlayerController():
    def __init__(self, paddle):
        self.paddle = paddle
        self.upkey = K_UP
        self.downkey = K_DOWN

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == self.upkey:
            self.paddle.up()
        elif event.type == KEYDOWN and event.key == self.downkey:
            self.paddle.down()
        elif event.type == KEYUP and (event.key in (self.upkey, self.downkey)):
            self.paddle.stop()
        else:
            return False
        return True


class AIController:
    def __init__(self, paddle):
        self.paddle = paddle

    def update(self):
        pass
