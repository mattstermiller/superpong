import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from pygame import Surface
from pygame import draw
from pygame.color import THECOLORS
from pygame.math import Vector2
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


class Table(PongSprite):
    def __init__(self):
        PongSprite.__init__(self)

        wallSize = 0.045
        wallColor = THECOLORS['white']
        centerLineColor = THECOLORS['red']

        self.size = Vector2(1.5, 1)
        self.innerSize = self.size.elementwise() - wallSize*2

        self.viewport.updateRect(self)

        pixelWallSize = self.viewport.translateSize((wallSize, wallSize))
        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        # draw center line
        lineDivisions = 15
        lineRect = Rect((0, 0), self.viewport.translateSize((0.005, 1/lineDivisions)))
        lineRect.centerx = self.rect.width/2
        for i in range(1, lineDivisions, 2):
            lineRect.y = lineRect.height*i
            self.image.fill(centerLineColor, lineRect)

        # draw walls
        self.image.fill(wallColor, Rect(0, 0, self.rect.width, pixelWallSize.y))
        self.image.fill(wallColor, Rect(0, self.rect.height - pixelWallSize.y, self.rect.width, pixelWallSize.y))


class Paddle(PongSprite):
    def __init__(self, table: Table, side: int):
        PongSprite.__init__(self)
        self.table = table
        self.side = side

        self.size = Vector2(0.024, 0.145)
        self.pos = Vector2()
        self.direction = 0
        self.reset()

        if self.side < 0:
            paddleColor = (32, 32, 240)
        else:
            paddleColor = (192, 32, 32)

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

        maxDist = self.table.innerSize.y/2 - self.size.y/2
        if self.pos.y > maxDist:
            self.pos.y = maxDist
        elif self.pos.y < -maxDist:
            self.pos.y = -maxDist

        self.viewport.updateRectPos(self)

    def up(self):
        self.direction = 1

    def down(self):
        self.direction = -1

    def stop(self):
        self.direction = 0


class Ball(PongSprite):
    def __init__(self, table: Table, paddles: []):
        PongSprite.__init__(self)
        self.table = table
        self.paddles = paddles

        self.radius = 0.01
        self.size = Vector2(self.radius*2, self.radius*2)
        self.pos = Vector2()
        self.vel = Vector2()
        self.reset()

        self.viewport.updateRect(self)

        self.image = Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        draw.ellipse(self.image, THECOLORS['white'], Rect((0, 0), self.rect.size))

    def reset(self):
        self.pos = Vector2()
        self.vel = Vector2(0.3, 0.2)

    def update(self):
        delta = 1/60
        move = self.vel*delta

        # move in small increments so that the ball cannot pass through objects when travelling quickly
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
        maxDist = self.table.innerSize.y/2 - self.radius
        if self.pos.y >= maxDist:
            self.pos.y = maxDist
            self.vel.y *= -1
        elif self.pos.y <= -maxDist:
            self.pos.y = -maxDist
            self.vel.y *= -1

        for p in self.paddles:
            projection = self.collide(p)
            if projection:
                self.pos += projection
                normal = collision.ellipticNormal(self.pos, p.pos, 4)
                # todo: take paddle's vel into account
                self.vel.reflect_ip(normal)
                return True

        return False
