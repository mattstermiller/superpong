import pygame
from pygame.locals import *
from pygame.sprite import Sprite
import assets
import controllers


class Table(Sprite):
    def __init__(self):
        Sprite.__init__(self)

        wallsize = 20
        wallcolor = color.THECOLORS['white']

        self.rect = Rect(0, 100, 800, 400)
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
            texcolor = (192, 32, 32)
        else:
            texcolor = (32, 32, 240)

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
        self.rect.move_ip(0, 10 * self.direction)
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

        self.rect = Rect(0, 0, 10, 10)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(color.THECOLORS['white'])

        self.vel = (50.0, 20.0)
        self.pos = self.rect.center = table.innerRect.center

    def update(self):
        delta = 1/60
        self.pos = tuple(p + v*delta for p, v in zip(self.pos, self.vel))
        self.rect.center = tuple(round(x) for x in self.pos)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill(color.THECOLORS['black'])

    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Super Pong 2015", 1, color.THECOLORS['white'])
        textpos = text.get_rect(center=(background.get_width() / 2, 50))
        background.blit(text, textpos)

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    table = Table()
    ball = Ball(table)
    paddle0 = Paddle(table, 0)
    paddle1 = Paddle(table, 1)
    sprites = pygame.sprite.RenderPlain(table, ball, paddle0, paddle1)

    player0 = controllers.PlayerController(paddle0, K_UP, K_DOWN)
    player1 = controllers.AIController(paddle1)

    while 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            elif player0.handle_event(event):
                pass

        player1.update()
        sprites.update()

        screen.blit(background, (0, 0))
        sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
