import pygame
from pygame.locals import *
import assets

table = Rect(0, 100, 800, 400)


class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = assets.load_image('paddle.png', -1)
        self.rect = self.image.get_rect(center=(100, 100))
        self.direction = 0

    def update(self):
        self.rect.move_ip(0, 10 * self.direction)
        self.rect.clamp_ip(table)

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
    paddle = Paddle()
    sprites = pygame.sprite.RenderPlain(paddle)

    while 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_UP:
                paddle.up()
            elif event.type == KEYDOWN and event.key == K_DOWN:
                paddle.down()
            elif event.type == KEYUP and (event.key == K_UP or event.key == K_DOWN):
                paddle.stop()

        sprites.update()

        screen.blit(background, (0, 0))
        sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
