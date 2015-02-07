from menu import *
from pong import *
from controllers import PlayerController, BotController
from enum import Enum


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


class GameState(Enum):
    mainMenu = 1
    pauseMenu = 2
    inGame = 3
    quit = 4


class StateManager:
    def __init__(self):
        self.current = GameState.mainMenu


class Game:
    def __init__(self, state: StateManager, conf: Config):
        self.state = state
        self.config = conf

        table = Table()
        self.paddles = [Paddle(table, -1), Paddle(table, 1)]
        self.ball = Ball(table, self.paddles)
        self.sprites = pygame.sprite.RenderPlain(table, self.ball, self.paddles[0], self.paddles[1])

        self.players = []
        self.bots = []

    def start(self, players: int):
        for sprite in [self.ball] + self.paddles:
            sprite.reset()

        self.players = [PlayerController(self.paddles[0], self.config, 1)]
        self.bots = []

        if players == 1:
            self.bots.append(BotController(self.paddles[1], self.ball))
        elif players == 2:
            self.players.append(PlayerController(self.paddles[1], self.config, 2))

    def handle_event(self, event: EventType) -> bool:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.state.current = GameState.pauseMenu
            return True

        for player in self.players:
            if player.handle_event(event):
                return True

        return False

    def update(self):
        for bot in self.bots:
            bot.update()

        self.sprites.update()


def createMenu(rootNode: MenuNode, screenSize: (int, int)) -> Menu:
    foreColor = THECOLORS['white']
    selectColor = (0, 0, 128)
    backgroundColor = (64, 64, 64, 192)
    borderColor = (255, 255, 255, 192)
    fadeColor = (128, 128, 128, 32)

    menu = Menu(rootNode, pygame.font.Font(None, 36), foreColor, selectColor, backgroundColor, borderColor, fadeColor)
    menu.midtop = (int(screenSize[0] / 2), int(screenSize[0] / 8))

    return menu


def getOptions(conf: Config) -> MenuNode:
    options = MenuNode("Options", key=K_o)

    video = MenuNode("Video", key=K_v)
    video.add(CheckMenuNode("Full Screen", key=K_f))
    video.add(MenuNode("Resolution", key=K_r))
    options.add(video)

    options.add(MenuNode("Audio", key=K_a))

    keys = MenuNode("Key Bindings", key=K_k)

    keys.add(KeyBindMenuNode("P1 Up", 'p1up', conf))
    keys.add(KeyBindMenuNode("P1 Down", 'p1down', conf))
    keys.add(KeyBindMenuNode("P2 Up", 'p2up', conf))
    keys.add(KeyBindMenuNode("P2 Down", 'p2down', conf))
    options.add(keys)

    return options


def getMainMenu(screenSize: (int, int), state: StateManager, conf: Config, game: Game) -> Menu:
    root = MenuNode("Super Pong 2015")

    newGame = MenuNode("New Game", key=K_n)

    def play1():
        game.start(1)
        state.current = GameState.inGame
        root.menu.reset()

    newGame.add(MenuNode("One Player", play1, K_o))

    def play2():
        game.start(2)
        state.current = GameState.inGame
        root.menu.reset()

    newGame.add(MenuNode("Two Players", play2, K_t))

    root.add(newGame)

    root.add(getOptions(conf))

    def exitGame():
        state.current = GameState.quit

    root.add(MenuNode("Exit", exitGame, K_x))

    return createMenu(root, screenSize)


def getPauseMenu(screenSize: (int, int), state: StateManager, conf: Config) -> Menu:
    root = MenuNode("Game Paused")

    def resume():
        state.current = GameState.inGame

    root.add(MenuNode("Resume", resume, K_r))

    root.add(getOptions(conf))

    def endGame():
        state.current = GameState.mainMenu
        root.menu.reset()

    root.add(MenuNode("End Game", endGame, K_e))

    def exitGame():
        state.current = GameState.quit

    root.add(MenuNode("Exit", exitGame, K_x))

    return createMenu(root, screenSize)


def main():
    # display
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill(THECOLORS['black'])

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    conf = Config('settings.config')
    conf.settings = {'p1up': K_w, 'p1down': K_s, 'p2up': K_UP, 'p2down': K_DOWN}
    conf.load()

    # viewport
    gameArea = Vector2(1.5, 1)
    screenArea = Rect(0, 0, 3, 2).fit(screen.get_rect())
    PongSprite.viewport = Viewport(screenArea, gameArea)

    state = StateManager()
    game = Game(state, conf)
    mainMenu = getMainMenu(screen.get_size(), state, conf, game)
    pauseMenu = getPauseMenu(screen.get_size(), state, conf)

    # game loop
    while state.current != GameState.quit:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.mod & KMOD_ALT and event.key == K_F4:
                state.current = GameState.quit
                break

            if state.current == GameState.mainMenu:
                mainMenu.handle_event(event)
            elif state.current == GameState.pauseMenu:
                pauseMenu.handle_event(event)
            elif state.current == GameState.inGame:
                game.handle_event(event)

        if state.current == GameState.quit:
            screen.fill(THECOLORS['black'])
            pygame.display.flip()
            break

        if state.current == GameState.inGame:
            game.update()

        screen.blit(background, (0, 0))
        game.sprites.draw(screen)

        if state.current == GameState.mainMenu:
            mainMenu.draw(screen)
        elif state.current == GameState.pauseMenu:
            pauseMenu.draw(screen)

        pygame.display.flip()


if __name__ == '__main__':
    main()
