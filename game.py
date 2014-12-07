import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame import draw
import assets
import controllers


class Table(Sprite):
    def __init__(self, rect):
        Sprite.__init__(self)

        wallsize = 20
        wallcolor = color.THECOLORS['white']

        self.rect = rect
        self.innerRect = self.rect.inflate(-wallsize*2, -wallsize*2)

        self.image = pygame.Surface(self.rect.size)
        self.image = self.image.convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.image.fill(wallcolor, Rect(0, 0, self.rect.width, wallsize))
        self.image.fill(wallcolor, Rect(0, self.rect.height - wallsize, self.rect.width, wallsize))


class Paddle(Sprite):
    def __init__(self, table, side):
        Sprite.__init__(self)
        self.table = table

        if side == 0:
            texcolor = (32, 32, 240)
        else:
            texcolor = (192, 32, 32)

        self.image = assets.load_image('paddle.png', colorize=texcolor)
        self.rect = self.image.get_rect()

        hoffset = 50
        if side == 0:
            self.rect.centerx = table.innerRect.left + hoffset
        else:
            self.rect.centerx = table.innerRect.right - hoffset
        self.rect.centery = table.innerRect.centery

        self.direction = 0

    def update(self):
        speed = 5
        self.rect.move_ip(0, speed * self.direction)
        self.rect.clamp_ip(self.table.innerRect)

    def up(self):
        self.direction = -1

    def down(self):
        self.direction = 1

    def stop(self):
        self.direction = 0


class Ball(Sprite):
    def __init__(self, table):
        Sprite.__init__(self)
        self.table = table

        self.radius = 6
        self.rect = Rect(0, 0, self.radius*2, self.radius*2)
        self.image = pygame.Surface(self.rect.size)
        draw.circle(self.image, color.THECOLORS['white'], (self.radius, self.radius), self.radius)

        self.vel = Vector2(50.0, 80.0)
        self.pos = self.rect.center = Vector2(table.innerRect.center)

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
            self._move(self.pos + incr)

    def _move(self, moveTo):
        if moveTo.y <= self.table.innerRect.top + self.radius:
            moveTo.y = self.table.innerRect.top + self.radius
            self.vel.y *= -1
        elif moveTo.y >= self.table.innerRect.bottom - self.radius:
            moveTo.y = self.table.innerRect.bottom - self.radius
            self.vel.y *= -1

        self.pos = moveTo
        self.rect.center = tuple(round(x) for x in self.pos)


def main():
    pygame.init()

    screenSize = (800, 600)
    screenAspect = screenSize[0] / screenSize[1]
    screen = pygame.display.set_mode(screenSize)

    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(0)

    # calculate usable area
    tableAspect = 1.5
    if screenAspect > tableAspect:
        # constrained by vertical space
        tableRect = Rect(0, 0, screenSize[1] * tableAspect, screenSize[1])
    else:
        tableRect = Rect(0, 0, screenSize[0], screenSize[0] / tableAspect)
    tableRect.center = Rect((0, 0), screenSize).center

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

    table = Table(tableRect)
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
