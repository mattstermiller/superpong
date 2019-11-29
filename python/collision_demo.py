from pygame.event import EventType
from sprites import *


class Demo:
    def __init__(self, screen):
        self.screen = screen
        self.isMovingBall = False
        self.isMovingVel = False

        self.table = Table()
        self.table.size = Vector2(1, 1)

        self.paddle = Paddle(self.table, -1)
        self.paddle.pos = Vector2(0, 0)
        self.paddle.size = self.paddle.size.elementwise()*2

        self.ball = Ball(self.table, [self.paddle], self)
        self.ball.size = self.ball.size.elementwise()*2
        self.ball.pos = Vector2(0.04, 0.1)
        self.ball.vel = Vector2(-0.2, 0)

        self.imageBallGhost = None

        self.sprites = pygame.sprite.OrderedUpdates(self.paddle, self.ball)

        screenArea = self.screen.get_rect()
        PongSprite.viewport = Viewport(screenArea, self.table.size)

        self.initImage()

    def initImage(self):
        for s in self.sprites:
            s.initImage()
            s.updateRectPos()

        self.imageBallGhost = Surface(self.ball.rect.size).convert_alpha()
        self.imageBallGhost.fill((0, 0, 0, 0))
        draw.ellipse(self.imageBallGhost, (160,)*3 + (225,), self.imageBallGhost.get_rect())


    def handle_event(self, event: EventType) -> bool:
        LEFT = 1
        RIGHT = 3

        def moveBall():
            self.ball.pos = PongSprite.viewport.getGamePos(event.pos)

        def moveVel():
            self.ball.vel = PongSprite.viewport.getGamePos(event.pos) - self.ball.pos

        if event.type == MOUSEBUTTONDOWN:
            if event.button == LEFT:
                self.isMovingBall = True
                moveBall()
            if event.button == RIGHT:
                self.isMovingVel = True
                moveVel()
        elif event.type == MOUSEBUTTONUP:
            if event.button == LEFT:
                self.isMovingBall = False
            if event.button == RIGHT:
                self.isMovingVel = False
        elif event.type == MOUSEMOTION:
            if self.isMovingBall:
                moveBall()
            if self.isMovingVel:
                moveVel()

    def update(self, delta: float):
        for sprite in self.sprites:
            sprite.updateRectPos()

    def draw(self):
        self.screen.fill(THECOLORS['black'])
        self.sprites.draw(self.screen)

        def screenPos(gamePos):
            return PongSprite.viewport.getScreenPos(gamePos)

        def drawLine(colr, p1, p2):
            pygame.draw.aaline(self.screen, colr, screenPos(p1), screenPos(p2))

        drawLine((0, 200, 0), self.ball.pos, self.ball.pos + self.ball.vel)

        projection = self.ball.collide(self.paddle)
        if projection:
            # calc ball position after projecting out of collision
            projPos = self.ball.pos + projection

            # draw ghost at projected position
            projRect = self.ball.rect.copy()
            projRect.center = screenPos(projPos)
            self.screen.blit(self.imageBallGhost, projRect)

            # draw surface normal
            normal = collision.ellipticNormal(projPos, self.paddle.pos, Ball.COLLISION_CURVE_EXPONENT)
            normal.scale_to_length(0.3)
            drawLine((0, 0, 255), projPos, projPos + normal)

            # draw reflected velocity
            reflectedVel = self.ball.vel.reflect(normal)
            drawLine((255, 255, 0), projPos, projPos + reflectedVel)


def main():
    pygame.init()

    pygame.display.set_caption('Super Pong Collision Demo')
    screen = pygame.display.set_mode((800, 800), DOUBLEBUF)
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
