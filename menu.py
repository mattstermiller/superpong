from pygame.locals import *
from pygame.constants import *
from pygame import Surface
from pygame.event import EventType
from pygame.font import Font


class MenuNode:
    def __init__(self, text: str, callback, key: int=None):
        self.text = text
        self.callback = callback
        self.key = key
        self.image = None
        self.rect = None

    def init(self, font: Font, fontColor: Color):
        self.image = font.render(self.text, 1, fontColor)
        self.rect = self.image.get_rect()

    def invoke(self):
        self.callback()

    def draw(self, screen: Surface, pos: (int, int)):
        drawRect = self.rect.copy()
        drawRect.center = pos
        screen.blit(self.image, drawRect)


class Menu:
    def __init__(self, rect: Rect, font: Font, fontColor: Color):
        self.nodes = []
        self.selected = 0

        self.font = font
        self.fontColor = fontColor

        self.rect = rect
        self.image = Surface(rect.size).convert_alpha()
        self.image.fill((128, 128, 128, 32))

    def add(self, node: MenuNode):
        self.nodes.append(node)
        node.init(self.font, self.fontColor)

    def handle_event(self, event: EventType):
        if event.type != KEYDOWN:
            return False

        if event.key == K_UP:
            if self.selected > 0:
                self.selected -= 1
            return True
        elif event.key == K_DOWN:
            if self.selected < len(self.nodes) - 1:
                self.selected += 1
            return True
        elif event.key == K_RETURN:
            self.nodes[self.selected].invoke()
            return True

        for node in self.nodes:
            if event.key == node.key:
                node.invoke()
                return True

    def draw(self, screen: Surface):
        screen.blit(self.image, (0, 0))

        pos = self.rect.center
        height = self.font.get_height()
        for i, node in enumerate(self.nodes):
            if i == self.selected:
                selectedRect = Rect((0, 0), node.rect.size)
                selectedRect.center = pos
                screen.fill((64, 64, 64), selectedRect)
            node.draw(screen, pos)
            pos = (pos[0], pos[1] + height)
