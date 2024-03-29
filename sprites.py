import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from pygame import Surface
from pygame import draw
from pygame.color import THECOLORS
from pygame.math import Vector2
from random import Random
import collision


class Viewport:
    def __init__(self, screenArea: Rect, cameraSize: (float, float), cameraCenter: (float, float)=(0, 0),
                 invertYAxis: bool=True):
        screenSize = Vector2(screenArea.size)
        screenPos = Vector2(screenArea.topleft)
        cameraSize = Vector2(cameraSize)
        cameraCenter = Vector2(cameraCenter)

        self.sizeFactor = screenSize.elementwise()/cameraSize
        self.posFactor = Vector2(self.sizeFactor)
        self.posTranslate = cameraSize/2 - cameraCenter
        screenTranslate = (screenPos.elementwise()*cameraSize).elementwise()/screenSize
        if invertYAxis:
            self.posFactor.y *= -1
            screenTranslate.y *= -1
            self.posTranslate.y -= cameraSize.y
        self.posTranslate = self.posTranslate + screenTranslate

    def getScreenSize(self, gameSize: (float, float)) -> Vector2:
        screenSize = Vector2(gameSize).elementwise() * self.sizeFactor
        return Vector2(tuple(round(z) for z in screenSize))

    def getScreenPos(self, gamePos: (float, float)) -> Vector2:
        screenPos = (Vector2(gamePos) + self.posTranslate).elementwise() * self.posFactor
        return Vector2(tuple(round(z) for z in screenPos))

    def getGameSize(self, screenSize: (int, int)) -> Vector2:
        return Vector2(screenSize).elementwise() / self.sizeFactor

    def getGamePos(self, screenPos: (int, int)) -> Vector2:
        return (Vector2(screenPos).elementwise() / self.posFactor) - self.posTranslate


class PongSprite(Sprite):
    viewport = None
    """:type: Viewport"""

    def __init__(self):
        Sprite.__init__(self)
        self.rect = Rect(0, 0, 0, 0)
        self.size = Rect(0, 0, 0, 0)
        self._halfSize = None
        self.pos = Vector2()
        self.vel = Vector2()

        self.image = None
        """:type: Surface"""

    @property
    def halfSize(self):
        if self._halfSize is None:
            self._halfSize = tuple(d/2 for d in self.size)
        return self._halfSize

    def initImage(self):
        pass

    def updateRect(self):
        self.rect.size = self.viewport.getScreenSize(self.size)
        self.updateRectPos()

    def updateRectPos(self):
        self.rect.center = self.viewport.getScreenPos(self.pos)

    def collide(self, other):
        return collision.rect_rect(self.pos, self.halfSize, other.pos, other.halfSize)


class Table(PongSprite):
    WALL_SIZE = 0.045

    def __init__(self):
        PongSprite.__init__(self)
        self.size = Vector2(1.5, 1)
        self.innerSize = self.size.elementwise() - self.WALL_SIZE*2

    def initImage(self):
        viewport = PongSprite.viewport

        wallColor = THECOLORS['white']
        centerLineColor = THECOLORS['red']

        PongSprite.updateRect(self)

        pixelWallSize = viewport.getScreenSize((self.WALL_SIZE, self.WALL_SIZE))
        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        # draw center line
        lineDivisions = 15
        lineRect = Rect((0, 0), viewport.getScreenSize((0.005, 1/lineDivisions)))
        lineRect.centerx = self.rect.width/2
        for i in range(1, lineDivisions, 2):
            lineRect.y = lineRect.height*i
            self.image.fill(centerLineColor, lineRect)

        # draw walls
        self.image.fill(wallColor, Rect(0, 0, self.rect.width, pixelWallSize.y))
        self.image.fill(wallColor, Rect(0, self.rect.height - pixelWallSize.y, self.rect.width, pixelWallSize.y))


class ScoreBoard(PongSprite):
    SCORE_LIMIT = 9

    def __init__(self):
        PongSprite.__init__(self)

        self.scores = [0, 0]
        self.winner = None

        self.size = Vector2(1, Table.WALL_SIZE)
        self.pos = Vector2(0, 0.5-(Table.WALL_SIZE/2))

        self.font = None
        self.messages = []
        self.scoreMessages = []
        self.winnerMessages = []
        self.prepareMessage = None

    def initImage(self):
        self.updateRect()

        heightPx = self.viewport.getScreenSize(self.size)[1]
        self.font = pygame.font.Font(None, int(heightPx))

        self.image = Surface(self.rect.size).convert_alpha()
        self._renderScores()

        # setup message sprites
        messageFont = pygame.font.Font(None, int(heightPx*3))

        def positionMsg(msg, side):
            msg.rect = msg.image.get_rect()
            pos = self.viewport.getScreenPos((0.55 * side, 0.4))
            if i == 0:
                msg.rect.topleft = pos
            else:
                msg.rect.topright = pos

        self.scoreMessages = []
        for (i, name) in enumerate(["Blue", "Red"]):
            msg = PongSprite()
            msg.image = messageFont.render("{} point!".format(name), True, Paddle.COLORS[i])
            positionMsg(msg, [-1, 1][i])
            self.scoreMessages.append(msg)

        self.winnerMessages = []
        for i in range(2):
            msg = PongSprite()
            msg.image = messageFont.render("Winner!", True, Paddle.COLORS[i])
            positionMsg(msg, [-1, 1][i])
            self.winnerMessages.append(msg)

        msg = PongSprite()
        msg.image = messageFont.render("Get Ready!", True, THECOLORS['white'])
        msg.rect = msg.image.get_rect()
        msg.rect.center = self.viewport.getScreenPos((0, 0))
        self.prepareMessage = msg

        oldMessages = self.messages
        self.messages = self.scoreMessages + self.winnerMessages + [self.prepareMessage]
        # restore visibility from old messages
        for msg, oldMsg in zip(self.messages, oldMessages):
            msg.add(oldMsg.groups())
            oldMsg.kill()

    def reset(self):
        self.scores = [0, 0]
        self.winner = None

        self._show(self.prepareMessage)

    def score(self, player: int):
        self.scores[player] += 1
        self._renderScores()

        if self.scores[player] < self.SCORE_LIMIT:
            self._show(self.scoreMessages[player])
        else:
            self.winner = player
            self._show(self.winnerMessages[player])

    def hideMessages(self):
        for msg in self.messages:
            msg.kill()

    def _show(self, sprite):
        sprite.add(self.groups()[0])

    def _renderScores(self):
        self.image.fill((0, 0, 0, 0))

        for i in range(2):
            img = self.font.render(str(self.scores[i]), True, THECOLORS['black'])
            imgRect = img.get_rect()
            x = 0 if i == 0 else self.rect.width - imgRect.width
            y = (self.rect.height - imgRect.height)/2
            self.image.blit(img, (x, y))


class Paddle(PongSprite):
    SPEED = 1.1
    COLORS = [(32, 32, 240), (192, 32, 32)]

    def __init__(self, table: Table, side: int):
        PongSprite.__init__(self)
        self.table = table
        self.side = side

        self.size = Vector2(0.024, 0.145)
        self.pos = Vector2()
        self.direction = 0
        self.reset()

    def initImage(self):
        paddleColor = self.COLORS[0 if self.side < 0 else 1]

        self.updateRect()

        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        endSize = (self.rect.width, self.rect.width)
        draw.ellipse(self.image, paddleColor, Rect((0, 0), endSize))
        draw.ellipse(self.image, paddleColor, Rect((0, self.rect.height-self.rect.width), endSize))
        middle = Rect(0, self.rect.width/2, self.rect.width, self.rect.height - self.rect.width)
        self.image.fill(paddleColor, middle)

        if self.side < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def reset(self):
        self.pos = Vector2(0.6 * self.side, 0)
        self.stop()

    def update(self, delta: float):
        speed = self.SPEED*delta
        self.pos.y += speed*self.direction

        maxYDist = self.table.innerSize.y/2 - self.size.y/2
        if self.pos.y > maxYDist:
            self.pos.y = maxYDist
        elif self.pos.y < -maxYDist:
            self.pos.y = -maxYDist

        self.updateRectPos()

    def up(self):
        self.direction = 1

    def down(self):
        self.direction = -1

    def stop(self):
        self.direction = 0


class Ball(PongSprite):
    START_SPEED = 0.85
    SPEEDUP = 0.15
    SPEEDUP_HITS = 10
    MAX_ANGLE = 86
    COLLISION_TIMEOUT = 0.1
    COLLISION_CURVE_EXPONENT = 5

    def __init__(self, table: Table, paddles: [], game):
        PongSprite.__init__(self)
        self.table = table
        self.paddles = paddles
        self.game = game
        self.rand = Random()

        self.radius = 0.01
        self.size = Vector2(self.radius*2, self.radius*2)
        self.pos = Vector2()
        self.vel = Vector2()
        self.speedupHits = 0
        self.collisionTimeout = 0

    def initImage(self):
        self.updateRect()

        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        draw.ellipse(self.image, THECOLORS['white'], Rect((0, 0), self.rect.size))

    def reset(self):
        self.pos = Vector2(-2, 0)
        self.vel = Vector2()
        self.speedupHits = 0

    def serve(self, direction: int=0):
        self.pos = Vector2()
        if direction == 0:
            direction = -1 if self.rand.random() < 0.5 else 1
        angle = 180 if direction < 0 else 0
        angle += self.rand.uniform(-80, 80)
        self.vel.from_polar((self.START_SPEED, angle))

    def update(self, delta: float):
        if self.collisionTimeout > 0:
            self.collisionTimeout -= delta

        move = self.vel*delta

        # move in small increments so that the ball cannot pass through objects when traveling quickly
        while move:
            incr = Vector2(move)
            if incr.length_squared() > self.radius**2:
                incr.scale_to_length(self.radius)
                move.scale_to_length(move.length() - self.radius)
            else:
                move = None
            self.pos = self.pos + incr
            if self._collision():
                break

        self.updateRectPos()

    def _collision(self) -> bool:
        # wall collision
        maxYDist = self.table.innerSize.y/2 - self.radius
        if self.pos.y >= maxYDist:
            self.pos.y = maxYDist
            self.vel.y *= -1
            self.collisionTimeout = 0
            return True
        elif self.pos.y <= -maxYDist:
            self.pos.y = -maxYDist
            self.vel.y *= -1
            self.collisionTimeout = 0
            return True

        # score
        maxXDist = self.table.size.x/2 + self.radius
        if self.pos.x >= maxXDist:
            self.vel = Vector2()
            self.game.score(0)
            return True
        elif self.pos.x <= -maxXDist:
            self.vel = Vector2()
            self.game.score(1)
            return True

        # paddle collision
        if self.collisionTimeout <= 0:
            for paddle in self.paddles:
                projection = self.collide(paddle)
                if projection:
                    self.pos = self.pos + projection
                    normal = collision.ellipticNormal(self.pos, paddle.pos, self.COLLISION_CURVE_EXPONENT)
                    self.vel.reflect_ip(normal)
                    self._hitPaddle()
                    return True

        return False

    def _hitPaddle(self):
        self._preventVerticalVel()
        self.collisionTimeout = self.COLLISION_TIMEOUT

        self.speedupHits += 1
        if self.speedupHits == self.SPEEDUP_HITS:
            polar = self.vel.as_polar()
            self.vel.from_polar((polar[0] + self.SPEEDUP, polar[1]))
            self.speedupHits = 0

    def _preventVerticalVel(self):
        # because waiting 5 minutes for the ball to cross the table is not fun
        def setAngle(a):
            self.vel.from_polar((self.vel.length(), a))

        angle = Vector2().angle_to(self.vel)
        if self.MAX_ANGLE < angle <= 90:
            setAngle(self.MAX_ANGLE)
        elif 90 < angle < 180 - self.MAX_ANGLE:
            setAngle(180 - self.MAX_ANGLE)
        elif -self.MAX_ANGLE > angle > -90:
            setAngle(-self.MAX_ANGLE)
        elif -90 >= angle > -180 + self.MAX_ANGLE:
            setAngle(-180 + self.MAX_ANGLE)
