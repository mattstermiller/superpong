import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from pygame import Surface
from pygame import draw
from pygame.color import THECOLORS
from pygame.math import Vector2
from random import Random
import collision


class PongSprite(Sprite):
    viewport = None

    def __init__(self):
        Sprite.__init__(self)
        self.rect = Rect(0, 0, 0, 0)
        self.size = Rect(0, 0, 0, 0)
        self._halfSize = None
        self.pos = Vector2()
        self.vel = Vector2()

    @property
    def halfSize(self):
        if self._halfSize is None:
            self._halfSize = tuple(d/2 for d in self.size)
        return self._halfSize

    def collide(self, other):
        return collision.rect_rect(self.pos, self.halfSize, other.pos, other.halfSize)


class Table:
    WALL_SIZE = 0.045

    def __init__(self):
        viewport = PongSprite.viewport

        wallColor = THECOLORS['white']
        centerLineColor = THECOLORS['red']

        self.pos = Vector2()
        self.size = Vector2(1.5, 1)
        self.innerSize = self.size.elementwise() - self.WALL_SIZE*2

        self.rect = Rect(0, 0, 0, 0)
        viewport.updateRect(self)

        pixelWallSize = viewport.translateSize((self.WALL_SIZE, self.WALL_SIZE))
        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        # draw center line
        lineDivisions = 15
        lineRect = Rect((0, 0), viewport.translateSize((0.005, 1/lineDivisions)))
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

        self.viewport.updateRect(self)

        heightPx = self.viewport.translateSize(self.size)[1]
        self.font = pygame.font.Font(None, int(heightPx))

        self.image = Surface(self.rect.size).convert_alpha()
        self._renderScores()

        # setup score message sprites
        messageFont = pygame.font.Font(None, int(heightPx*3))

        self.scoreMessages = []
        names = ["Blue", "Red"]
        for i in range(2):
            msg = PongSprite()
            msg.image = messageFont.render("{} point!".format(names[i]), True, Paddle.COLORS[i])

            msg.rect = msg.image.get_rect()
            pos = self.viewport.translatePos((0.55 * [-1, 1][i], 0.4))
            if i == 0:
                msg.rect.topleft = pos
            else:
                msg.rect.topright = pos

            self.scoreMessages.append(msg)

    def _renderScores(self):
        self.image.fill((0, 0, 0, 0))

        for i in range(2):
            img = self.font.render(str(self.scores[i]), True, THECOLORS['black'])
            imgRect = img.get_rect()
            x = 0 if i == 0 else self.rect.width - imgRect.width
            y = (self.rect.height - imgRect.height)/2
            self.image.blit(img, (x, y))

    def score(self, playerNum: int):
        self.scores[playerNum] += 1
        self._renderScores()

        if self.scores[playerNum] < self.SCORE_LIMIT:
            self.scoreMessages[playerNum].add(self.groups()[0])

            # set timer to remove score message and reset ball
            pass
        else:
            self.winner = playerNum


class Paddle(PongSprite):
    COLORS = [(32, 32, 240), (192, 32, 32)]

    def __init__(self, table: Table, side: int):
        PongSprite.__init__(self)
        self.table = table
        self.side = side

        self.size = Vector2(0.024, 0.145)
        self.pos = Vector2()
        self.direction = 0
        self.reset()

        paddleColor = self.COLORS[0 if self.side < 0 else 1]

        self.viewport.updateRect(self)

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

    def update(self):
        delta = 1/60
        speed = 0.6*delta
        self.pos.y += speed*self.direction

        maxYDist = self.table.innerSize.y/2 - self.size.y/2
        if self.pos.y > maxYDist:
            self.pos.y = maxYDist
        elif self.pos.y < -maxYDist:
            self.pos.y = -maxYDist

        self.viewport.updateRectPos(self)

    def up(self):
        self.direction = 1

    def down(self):
        self.direction = -1

    def stop(self):
        self.direction = 0


class Ball(PongSprite):
    def __init__(self, table: Table, paddles: [], scoreBoard: ScoreBoard):
        PongSprite.__init__(self)
        self.table = table
        self.paddles = paddles
        self.scoreBoard = scoreBoard
        self.rand = Random()

        self.radius = 0.01
        self.size = Vector2(self.radius*2, self.radius*2)
        self.pos = Vector2()
        self.vel = Vector2()
        self.reset()

        self.viewport.updateRect(self)

        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        draw.ellipse(self.image, THECOLORS['white'], Rect((0, 0), self.rect.size))

    def reset(self, dir: int=0):
        self.pos = Vector2()
        if dir == 0:
            dir = -1 if self.rand.random() < 0.5 else 1
        angle = 180 if dir < 0 else 0
        self.vel = collision.vectorFromPolar((0.4, self.rand.gauss(angle, 27)))

    def update(self):
        delta = 1/60
        move = self.vel*delta

        # move in small increments so that the ball cannot pass through objects when traveling quickly
        while move:
            incr = Vector2(move)
            if incr.length_squared() > self.radius**2:
                incr.scale_to_length(self.radius)
                move.scale_to_length(move.length() - self.radius)
            else:
                move = None
            self.pos += incr
            if self._collide():
                break

        self.viewport.updateRectPos(self)

    def _collide(self) -> bool:
        # wall collision
        maxYDist = self.table.innerSize.y/2 - self.radius
        if self.pos.y >= maxYDist:
            self.pos.y = maxYDist
            self.vel.y *= -1
        elif self.pos.y <= -maxYDist:
            self.pos.y = -maxYDist
            self.vel.y *= -1

        # score
        maxXDist = self.table.size.x/2 + self.radius
        if self.pos.x >= maxXDist:
            self.vel = Vector2()
            self.scoreBoard.score(0)
        elif self.pos.x <= -maxXDist:
            self.vel = Vector2()
            self.scoreBoard.score(1)

        # paddle collision
        for p in self.paddles:
            projection = self.collide(p)
            if projection:
                self.pos += projection
                normal = collision.ellipticNormal(self.pos, p.pos, 4)
                # todo: take paddle's vel into account
                self.vel.reflect_ip(normal)
                return True

        return False
