import pygame
from pygame.locals import *
from pygame.math import Vector2
from pong import PongSprite, Table, Paddle, Ball
from controllers import PlayerController, BotController


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


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(False)

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
    PongSprite.viewport = Viewport(screenArea, gameArea)

    table = Table()
    ball = Ball(table)
    paddle0 = Paddle(table, 0)
    paddle1 = Paddle(table, 1)
    sprites = pygame.sprite.RenderPlain(table, ball, paddle0, paddle1)

    players = [PlayerController(paddle0, K_w, K_s)]
    bots = [BotController(paddle1, ball)]
    # players = [PlayerController(paddle0, K_w, K_s), PlayerController(paddle1, K_UP, K_DOWN)]
    # bots = []

    while True:
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
