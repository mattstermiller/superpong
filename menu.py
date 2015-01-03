from pygame.locals import *
from pygame.constants import *
from pygame import Surface
from pygame.event import EventType
from pygame.font import Font


# forward declarations for type annotations
class MenuNode:
    pass
class Menu:
    pass


class MenuNode:
    def __init__(self, text: str, callback=None, key: int=None):
        self.text = text
        self.callback = callback
        self.key = key
        self.menu = None
        """:type: Menu"""
        self.parent = None
        """:type: MenuNode"""
        self.image = None
        """:type: Surface"""
        self.rect = None
        """:type: Rect"""

        self.nodes = []
        self.selected = 0

    def init(self, menu):
        self.menu = menu
        self.image = menu.font.render(self.text, 1, menu.fontColor)
        self.rect = self.image.get_rect()
        for node in self.nodes:
            node.init(menu)

    def add(self, node: MenuNode):
        self.nodes.append(node)
        node.parent = self
        if self.menu is not None:
            node.init(self.menu)

    def handle_event(self, event: EventType) -> bool:
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
        elif event.key == K_ESCAPE:
            if self.parent:
                self.menu.current = self.parent
            return True

        for node in self.nodes:
            if event.key == node.key:
                node.invoke()
                return True

    def invoke(self):
        if len(self.nodes) > 0:
            self.menu.current = self
        elif self.callback:
            self.callback()

    def draw(self, screen: Surface, pos: (int, int)):
        drawRect = self.rect.copy()
        drawRect.midtop = pos
        screen.blit(self.image, drawRect)

    def drawMenu(self, screen: Surface):
        pos = list(self.menu.midtop)

        def advance(positions: int=1):
            pos[1] += (self.menu.fontHeight + self.menu.fontPadding)*positions

        advance()
        self.draw(screen, pos)
        advance(2)

        for i, node in enumerate(self.nodes):
            if i == self.selected:
                selectedRect = node.rect.copy()
                selectedRect.midtop = pos
                selectedRect.inflate_ip(self.menu.fontPadding*2, self.menu.fontPadding)
                screen.fill((self.menu.selectColor), selectedRect)
            node.draw(screen, pos)
            advance()


class Menu:
    def __init__(self, node: MenuNode, midtop: (int, int), font: Font, fontColor: Color, selectColor: Color,
                 backgroundColor: Color=None, borderColor: Color=None, fadeColor: Color=None):
        self.current = node

        self.midtop = midtop
        self.font = font
        self.fontColor = fontColor
        self.fontHeight = font.get_height()
        self.fontPadding = int(self.fontHeight/4)
        self.selectColor = selectColor
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.fadeColor = fadeColor
        self.imageInited = False

        node.init(self)

    def handle_event(self, event: EventType) -> bool:
        if event.type != KEYDOWN:
            return False

        self.current.handle_event(event)

    def draw(self, screen: Surface):
        if not self.imageInited:
            self._initImage(screen)

        if self.image:
            screen.blit(self.image, self.imageRect)
        self.current.drawMenu(screen)

    def _initImage(self, screen: Surface):
        self.imageInited = True

        if self.backgroundColor:
            # search for largest node count in tree
            def visit(n: MenuNode) -> int:
                sizes = [len(n.nodes)]
                for c in n.nodes:
                    sizes.append(visit(c))
                return max(sizes)

            node = self.current
            while node.parent:
                node = node.parent

            maxItems = visit(node)

            # include room for border top and bottom, menu header, and header padding
            size = (400, (self.fontHeight + self.fontPadding) * (maxItems + 4))

            import drawutil
            self.image = drawutil.rect(size, self.backgroundColor, int(self.fontHeight / 2), self.borderColor)
            self.imageRect = Rect((0, 0), size)
            self.imageRect.midtop = self.midtop

        if self.fadeColor:
            fade = Surface(screen.get_size())

            if len(self.fadeColor) > 3:
                fade = fade.convert_alpha()
            else:
                fade = fade.convert()

            fade.fill(self.fadeColor)

            fade.blit(self.image, self.imageRect)
            self.image = fade
            self.imageRect = self.image.get_rect()
