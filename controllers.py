from pygame.constants import *


class PlayerController():
    def __init__(self, paddle, upKey, downKey):
        self.paddle = paddle
        self.upKey = upKey
        self.downKey = downKey
        self.upPressed = False
        self.downPressed = False

    def handle_event(self, event):
        if not event.type in [KEYDOWN, KEYUP]:
            return False

        if event.key == self.upKey:
            self.upPressed = event.type == KEYDOWN
        elif event.key == self.downKey:
            self.downPressed = event.type == KEYDOWN
        else:
            return False

        if self.upPressed and not self.downPressed:
            self.paddle.up()
        elif self.downPressed and not self.upPressed:
            self.paddle.down()
        else:
            self.paddle.stop()
        return True


class BotController:
    def __init__(self, paddle, ball):
        self.paddle = paddle
        self.ball = ball

    def update(self):
        threshhold = 10
        diff = self.ball.rect.centery - self.paddle.rect.centery
        if diff > threshhold:
            self.paddle.down()
        elif diff < -threshhold:
            self.paddle.up()
        else:
            self.paddle.stop()
