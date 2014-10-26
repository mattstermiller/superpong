import pygame
from pygame.locals import *
from pygame.sprite import Sprite
import assets

table = None


class Table(Sprite):
    def __init__(self):
        Sprite.__init__(self)

        wallsize = 20

        self.rect = Rect(0, 100, 800, 400)
        self.innerRect = self.rect.inflate(-wallsize*2, -wallsize*2)

        self.image = pygame.Surface(self.rect.size)
        self.image = self.image.convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.image.fill((255, 255, 255), Rect(0, 0, self.rect.width, wallsize))
        self.image.fill((255, 255, 255), Rect(0, self.rect.height - wallsize, self.rect.width, wallsize))


class Paddle(Sprite):
    def __init__(self, side):
        Sprite.__init__(self)

        if side == 0:
            color = (192, 32, 32)
        else:
            color = (32, 32, 240)

        self.image = assets.load_image('paddle.png', colorize=color)
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
        self.rect.clamp_ip(table.innerRect)

    def up(self):
        self.direction = -1

    def down(self):
        self.direction = 1

    def stop(self):
        self.direction = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill((0, 0, 0))

    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Super Pong 2015", 1, (255, 255, 255))
        textpos = text.get_rect(center=(background.get_width() / 2, 50))
        background.blit(text, textpos)

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    global table
    table = Table()
    paddle0 = Paddle(0)
    paddle1 = Paddle(1)
    sprites = pygame.sprite.RenderPlain(paddle0, paddle1, table)

    while 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_UP:
                paddle0.up()
            elif event.type == KEYDOWN and event.key == K_DOWN:
                paddle0.down()
            elif event.type == KEYUP and (event.key == K_UP or event.key == K_DOWN):
                paddle0.stop()

        sprites.update()

        screen.blit(background, (0, 0))
        sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
