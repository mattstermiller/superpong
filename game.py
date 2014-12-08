import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame import draw
import controllers


class Viewport:
    def __init__(self, screenArea, cameraSize, cameraCenter=(0, 0), invertYAxis = True):
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
        self.posTranslate += screenTranslate

    def translateSize(self, size):
        pixelSize = Vector2(size).elementwise()*self.sizeFactor
        return Vector2(tuple(round(z) for z in pixelSize))

    def translatePos(self, pos):
        pixelPos = (Vector2(pos) + self.posTranslate).elementwise() * self.posFactor
        return Vector2(tuple(round(z) for z in pixelPos))

    def updateRect(self, sprite):
        if not hasattr(sprite, 'rect'):
            sprite.rect = Rect(0, 0, 1, 1)
        sprite.rect.size = self.translateSize(sprite.size)
        self.updateRectPos(sprite)

    def updateRectPos(self, sprite):
        sprite.rect.center = self.translatePos(sprite.pos)


class Table(Sprite):
    def __init__(self):
        Sprite.__init__(self)

        wallSize = 0.045
        wallColor = color.THECOLORS['white']
        centerLineColor = color.THECOLORS['red']

        self.size = Vector2(1.5, 1)
        self.innerSize = self.size.elementwise() - wallSize*2
        self.pos = Vector2()

        viewport.updateRect(self)

        pixelWallSize = viewport.translateSize((wallSize, wallSize))
        self.image = pygame.Surface(self.rect.size).convert_alpha()
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


class Paddle(Sprite):
    def __init__(self, table, side):
        Sprite.__init__(self)
        self.table = table

        self.size = Vector2(0.024, 0.145)
        self.pos = Vector2(-0.6, 0)
        self.direction = 0

        if side == 0:
            paddleColor = (32, 32, 240)
        else:
            paddleColor = (192, 32, 32)
            self.pos.x *= -1

        viewport.updateRect(self)

        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        endSize = (self.rect.width, self.rect.width)
        draw.ellipse(self.image, paddleColor, Rect((0, 0), endSize))
        draw.ellipse(self.image, paddleColor, Rect((0, self.rect.height-self.rect.width), endSize))
        middle = Rect(0, self.rect.width/2, self.rect.width, self.rect.height - self.rect.width)
        self.image.fill(paddleColor, middle)

    def update(self):
        delta = 1/60
        speed = 0.6*delta
        self.pos.y += speed*self.direction

        maxDist = self.table.innerSize.y/2 - self.size.y/2
        if self.pos.y > maxDist:
            self.pos.y = maxDist
        elif self.pos.y < -maxDist:
            self.pos.y = -maxDist

        viewport.updateRectPos(self)

    def up(self):
        self.direction = 1

    def down(self):
        self.direction = -1

    def stop(self):
        self.direction = 0


class Ball(Sprite):
    def __init__(self, table):
        Sprite.__init__(self)
        self.table = table

        self.radius = 0.01
        self.size = Vector2(self.radius*2, self.radius*2)
        self.pos = Vector2()

        self.vel = Vector2(0.1, 0.3)

        viewport.updateRect(self)

        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        draw.ellipse(self.image, color.THECOLORS['white'], Rect((0, 0), self.rect.size))

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
            self._collide()

        viewport.updateRectPos(self)

    def _collide(self):
        maxDist = self.table.innerSize.y/2 - self.radius
        if self.pos.y >= maxDist:
            self.pos.y = maxDist
            self.vel.y *= -1
        elif self.pos.y <= -maxDist:
            self.pos.y = -maxDist
            self.vel.y *= -1


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill(color.THECOLORS['black'])

    # if pygame.font:
        # font = pygame.font.Font(None, 36)
        # text = font.render("Super Pong 2015", 1, color.THECOLORS['white'])
        # textpos = text.get_rect(center=(background.get_width() / 2, 50))
        # background.blit(text, textpos)

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    gameArea = Vector2(1.5, 1)
    screenArea = Rect(0, 0, 3, 2).fit(screen.get_rect())
    global viewport
    viewport = Viewport(screenArea, gameArea)

    table = Table()
    ball = Ball(table)
    paddle0 = Paddle(table, 0)
    paddle1 = Paddle(table, 1)
    sprites = pygame.sprite.RenderPlain(table, ball, paddle0, paddle1)

    players = [controllers.PlayerController(paddle0, K_w, K_s)]
    bots = [controllers.BotController(paddle1, ball)]
    # players = [controllers.PlayerController(paddle0, K_w, K_s), controllers.PlayerController(paddle1, K_UP, K_DOWN)]
    # bots = []

    while 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return

            for player in players:
                if player.handle_event(event):
                    break

        for bot in bots:
            bot.update()

        sprites.update()

        screen.blit(background, (0, 0))
        sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
