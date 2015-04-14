from menu import *
from sprites import *
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
        self.posTranslate = self.posTranslate + screenTranslate

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
    mainMenu = 1
    pauseMenu = 2
    inGame = 3
    quit = 4


class Game:
    def __init__(self, config: Config):
        self.config = config
        self.screen = None
        """:type: Surface"""
        self.image = None
        """:type: Surface"""

        self.state = GameState.mainMenu

        self.table = Table()
        self.scoreBoard = ScoreBoard()
        self.paddles = [Paddle(self.table, -1), Paddle(self.table, 1)]
        self.ball = Ball(self.table, self.paddles, self)
        self.sprites = pygame.sprite.RenderPlain(self.scoreBoard, self.ball, self.paddles[0], self.paddles[1])

        self.players = []
        self.bots = []
        self.timers = []

        self.mainMenu = None
        self.pauseMenu = None

        self.initVideo()

        self.mainMenu = getMainMenu(self, config)
        self.pauseMenu = getPauseMenu(self, config)

    def initVideo(self):
        flags = DOUBLEBUF | HWSURFACE
        if self.config['fullscreen']:
            flags |= FULLSCREEN
        else:
            flags |= RESIZABLE
        self.screen = pygame.display.set_mode(self.config['resolution'], flags)

        size = self.screen.get_size()
        for menu in [self.mainMenu, self.pauseMenu]:
            if menu:
                menu.midtop = (int(size[0] / 2), int(size[0] / 8))
                menu.initImage(size)

        gameArea = Vector2(1.5, 1)
        screenArea = Rect(0, 0, 3, 2).fit(self.screen.get_rect())
        PongSprite.viewport = Viewport(screenArea, gameArea)

        self.image = pygame.Surface(size).convert()
        self.image.fill(THECOLORS['black'])

        self.table.initImage()
        self.image.blit(self.table.image, self.table.rect)

        for s in self.sprites:
            s.initImage()

    def start(self, players: int):
        self.state = GameState.inGame

        for sprite in self.paddles + [self.ball, self.scoreBoard]:
            sprite.reset()

        self.players = [PlayerController(self.paddles[0], self.config, 0)]
        self.bots = []

        if players == 1:
            self.bots.append(BotController(self.paddles[1], self.ball))
        elif players == 2:
            self.players.append(PlayerController(self.paddles[1], self.config, 1))

        self.timers.append(Timer(3, self._serveBall))

    def score(self, player: int):
        self.scoreBoard.score(player)

        if self.scoreBoard.winner is None:
            self.timers.append(Timer(3, lambda: self._serveBall(player)))

    def handle_event(self, event: EventType) -> bool:
        if event.type == VIDEORESIZE:
            self.config['resolution'] = event.size
            self.initVideo()
            self.config.save()
            return True

        if self.state == GameState.inGame:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.state = GameState.pauseMenu
                return True

            for player in self.players:
                if player.handle_event(event):
                    return True

        elif self.state == GameState.mainMenu:
            return self.mainMenu.handle_event(event)
        elif self.state == GameState.pauseMenu:
            return self.pauseMenu.handle_event(event)

        return False

    def update(self, delta: float):
        if self.state == GameState.inGame:
            for timer in self.timers:
                timer.tick(delta)
                if timer.isElapsed:
                    self.timers.remove(timer)

            for bot in self.bots:
                bot.update(delta)

            self.sprites.update(delta)
        elif self.state == GameState.mainMenu:
            self.mainMenu.update(delta)
        elif self.state == GameState.pauseMenu:
            self.pauseMenu.update(delta)

    def draw(self):
        if self.state == GameState.quit:
            self.screen.fill(THECOLORS['black'])
        else:
            self.screen.blit(self.image, (0, 0))

            self.sprites.draw(self.screen)

            if self.state == GameState.mainMenu:
                self.mainMenu.draw(self.screen)
            elif self.state == GameState.pauseMenu:
                self.pauseMenu.draw(self.screen)

    def _serveBall(self, scoringPlayer: int=None):
        self.scoreBoard.hideMessages()

        if scoringPlayer == 0:
            direction = 1
        elif scoringPlayer == 1:
            direction = -1
        else:
            direction = 0
        self.ball.serve(direction)


class Timer:
    def __init__(self, timeoutSeconds: float, action):
        self.timeoutSeconds = timeoutSeconds
        self.remaining = timeoutSeconds
        self.action = action

    @property
    def isElapsed(self):
        return self.remaining <= 0

    def tick(self, elapsedSeconds: float):
        self.remaining -= elapsedSeconds
        if self.isElapsed:
            self.action()

    def reset(self):
        self.remaining = self.timeoutSeconds


def createMenu(rootNode: MenuNode, screenSize: (int, int)) -> Menu:
    foreColor = THECOLORS['white']
    selectColor = (0, 0, 128)
    backgroundColor = (64, 64, 64, 192)
    borderColor = (255, 255, 255, 192)
    fadeColor = (128, 128, 128, 32)

    menu = Menu(rootNode, pygame.font.Font(None, 36), foreColor, selectColor, backgroundColor, borderColor, fadeColor)
    menu.midtop = (int(screenSize[0] / 2), int(screenSize[1] / 8))

    return menu


def getOptions(game: Game, conf: Config) -> MenuNode:
    options = MenuNode("Options", key=K_o)

    video = MenuNode("Video", key=K_v)

    fullscreenToSet = conf['fullscreen']
    resolutionToSet = conf['resolution']

    def setFull():
        nonlocal fullscreenToSet
        nonlocal resolutionToSet
        fullscreenToSet = fullscreen.checked
        resolution.disabled = not fullscreen.checked
        apply.disabled = False

    fullscreen = CheckMenuNode("Full Screen", setFull, K_f)
    fullscreen.checked = conf['fullscreen']

    video.add(fullscreen)

    resolution = MenuNode("Resolution", key=K_r)
    resolution.disabled = not fullscreen.checked

    def setRes(r):
        nonlocal resolutionToSet
        resolutionToSet = r
        apply.disabled = False

    for res in pygame.display.list_modes():
        node = RadioMenuNode("{}x{}".format(*res), lambda r=res: setRes(r))
        if fullscreen.checked:
            if res == conf['resolution']:
                node.checked = True
        else:
            if len(resolution.nodes) == 0:
                node.checked = True
        resolution.add(node)

    video.add(resolution)

    def applyChanges():
        nonlocal fullscreenToSet
        nonlocal resolutionToSet
        # if switching to fullscreen without setting a resolution, automatically use best mode
        if fullscreenToSet and not conf['fullscreen'] and resolutionToSet == conf['resolution']:
            resolutionToSet = pygame.display.list_modes()[0]
        conf['fullscreen'] = fullscreenToSet
        conf['resolution'] = resolutionToSet
        game.initVideo()
        conf.save()
        apply.disabled = True

    apply = MenuNode('Apply Changes', applyChanges, K_a)
    apply.disabled = True

    video.add(apply)

    options.add(video)

    options.add(MenuNode("Audio", key=K_a))

    keys = MenuNode("Key Bindings", key=K_k)

    keys.add(KeyBindMenuNode("P1 Up", 'p1up', conf))
    keys.add(KeyBindMenuNode("P1 Down", 'p1down', conf))
    keys.add(KeyBindMenuNode("P2 Up", 'p2up', conf))
    keys.add(KeyBindMenuNode("P2 Down", 'p2down', conf))
    options.add(keys)

    return options


def getMainMenu(game: Game, conf: Config) -> Menu:
    root = MenuNode("Super Pong 2015")

    newGame = MenuNode("New Game", key=K_n)

    def play(players: int):
        game.start(players)
        root.menu.reset()

    newGame.add(MenuNode("1 Player", lambda: play(1), K_1))
    newGame.add(MenuNode("2 Players", lambda: play(2), K_2))

    root.add(newGame)

    root.add(getOptions(game, conf))

    def exitGame():
        game.state = GameState.quit

    root.add(MenuNode("Exit", exitGame, K_x))

    return createMenu(root, conf['resolution'])


def getPauseMenu(game: Game, conf: Config) -> Menu:
    root = MenuNode("Game Paused")

    def resume():
        game.state = GameState.inGame

    root.add(MenuNode("Resume", resume, K_r))

    root.add(getOptions(game, conf))

    def endGame():
        game.state = GameState.mainMenu
        root.menu.reset()

    root.add(MenuNode("End Game", endGame, K_e))

    def exitGame():
        game.state = GameState.quit

    root.add(MenuNode("Exit", exitGame, K_x))

    return createMenu(root, conf['resolution'])


def main():
    conf = Config('settings.config')
    # default settings
    conf.settings = {'p1up': K_w, 'p1down': K_s, 'p2up': K_UP, 'p2down': K_DOWN, 'resolution': (800, 600)}
    conf.load()

    # display
    pygame.init()
    game = Game(conf)

    pygame.display.set_caption('Super Pong 2015')
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()

    # game loop
    while game.state != GameState.quit:
        delta = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.mod & KMOD_ALT and event.key == K_F4:
                game.state = GameState.quit
                break

            game.handle_event(event)

        game.update(delta)
        game.draw()

        pygame.display.flip()


if __name__ == '__main__':
    main()
