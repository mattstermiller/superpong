from pygame.constants import *
from pygame.event import EventType
from pong import Paddle, Ball


class PlayerController():
    def __init__(self, paddle: Paddle, upKey: int, downKey: int):
        self.paddle = paddle
        self.upKey = upKey
        self.downKey = downKey
        self.upPressed = False
        self.downPressed = False

    def handle_event(self, event: EventType) -> bool:
        if event.type not in [KEYDOWN, KEYUP]:
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
    def __init__(self, paddle: Paddle, ball: Ball):
        self.paddle = paddle
        self.ball = ball

    def update(self):
        threshhold = 0.01
        diff = self.ball.pos.y - self.paddle.pos.y
        if diff > threshhold:
            self.paddle.up()
        elif diff < -threshhold:
            self.paddle.down()
        else:
            self.paddle.stop()
