from menu import *
from pong import *
from controllers import PlayerController, BotController


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
        self.posTranslate += screenTranslate

    def translateSize(self, size: (float, float)) -> Vector2:
        pixelSize = Vector2(size).elementwise()*self.sizeFactor
        return Vector2(tuple(round(z) for z in pixelSize))

    def translatePos(self, pos: (float, float)) -> Vector2:
        pixelPos = (Vector2(pos) + self.posTranslate).elementwise() * self.posFactor
        return Vector2(tuple(round(z) for z in pixelPos))

    def updateRect(self, sprite: PongSprite):
        sprite.rect.size = self.translateSize(sprite.size)
        self.updateRectPos(sprite)

    def updateRectPos(self, sprite: PongSprite):
        sprite.rect.center = self.translatePos(sprite.pos)


class GameState:
    def __init__(self):
        self.isRunning = True
        self.inMenu = True


def setupMenu(state: GameState, screenSize: (int, int)) -> Menu:
    root = MenuNode("Super Pong 2015")
    menu = Menu(root, (int(screenSize[0]/2), 100), pygame.font.Font(None, 36), color.THECOLORS['white'],
                (0, 0, 128), (64, 64, 64, 192), (255, 255, 255, 192), (128, 128, 128, 32))

    def resume():
        state.inMenu = False
    root.add(MenuNode("Resume", resume, K_c))

    def exit():
        state.isRunning = False
    root.add(MenuNode("Exit", exit, K_e))

    return menu


def main():
    # display
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill(color.THECOLORS['black'])

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    # viewport
    gameArea = Vector2(1.5, 1)
    screenArea = Rect(0, 0, 3, 2).fit(screen.get_rect())
    PongSprite.viewport = Viewport(screenArea, gameArea)

    # game sprites
    table = Table()
    ball = Ball(table)
    paddle0 = Paddle(table, 0)
    paddle1 = Paddle(table, 1)
    sprites = pygame.sprite.RenderPlain(table, ball, paddle0, paddle1)

    players = [PlayerController(paddle0, K_w, K_s)]
    bots = [BotController(paddle1, ball)]

    # menu
    state = GameState()
    menu = setupMenu(state, screen.get_size())

    # game loop
    while state.isRunning:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                state.isRunning = False

            if state.inMenu:
                menu.handle_event(event)
            else:
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    state.inMenu = True
                    continue

                for player in players:
                    if player.handle_event(event):
                        break

        if not state.inMenu:
            for bot in bots:
                bot.update()

            sprites.update()

        screen.blit(background, (0, 0))
        sprites.draw(screen)

        if state.inMenu:
            menu.draw(screen)

        pygame.display.flip()


if __name__ == '__main__':
    main()
