from pygame.constants import *
from pygame.event import EventType
from sprites import Paddle, Ball
from config import Config


class PlayerController():
    def __init__(self, paddle: Paddle, config: Config, playerNum: int):
        self.paddle = paddle
        self.upPressed = False
        self.downPressed = False

        def setUp(key):
            self.upKey = key
        def setDown(key):
            self.downKey = key

        config.subscribe('p{}up'.format(playerNum + 1), setUp)
        config.subscribe('p{}down'.format(playerNum + 1), setDown)

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

    def update(self, delta: float):
        threshold = 0.01
        diff = self.ball.pos.y - self.paddle.pos.y
        if diff > threshold:
            self.paddle.up()
        elif diff < -threshold:
            self.paddle.down()
        else:
            self.paddle.stop()
