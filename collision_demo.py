from pygame.event import EventType
from sprites import *


class Demo:
    def __init__(self, screen):
        self.screen = screen
        self.mouseDown = False

        self.table = Table()
        self.table.size = Vector2(1, 1)

        self.paddle = Paddle(self.table, -1)
        self.paddle.pos.x = -0.3
        self.paddle.size = self.paddle.size.elementwise()*2

        self.ball = Ball(self.table, [self.paddle], self)
        self.ball.size = self.ball.size.elementwise()*2

        self.sprites = pygame.sprite.RenderPlain(self.ball, self.paddle)

        screenArea = self.screen.get_rect()
        PongSprite.viewport = Viewport(screenArea, self.table.size)

        for s in self.sprites:
            s.initImage()

    def handle_event(self, event: EventType) -> bool:
        if event.type == MOUSEBUTTONDOWN:
            self.mouseDown = True
            self.ball.pos = PongSprite.viewport.getGamePos(event.pos)
        elif event.type == MOUSEBUTTONUP:
            self.mouseDown = False
        elif event.type == MOUSEMOTION:
            if self.mouseDown:
                self.ball.pos = PongSprite.viewport.getGamePos(event.pos)

    def update(self, delta: float):
        self.sprites.update(delta)

    def draw(self):
        self.screen.fill(THECOLORS['black'])
        self.sprites.draw(self.screen)


def main():
    pygame.init()

    pygame.display.set_caption('Super Pong Collision Demo')
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF | HWSURFACE)
    clock = pygame.time.Clock()

    demo = Demo(screen)

    # game loop
    running = True
    while running:
        delta = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and \
                    (event.key == K_ESCAPE or event.mod & KMOD_ALT and event.key == K_F4):
                running = False
                break

            demo.handle_event(event)

        demo.update(delta)
        demo.draw()

        pygame.display.flip()


if __name__ == '__main__':
    main()
