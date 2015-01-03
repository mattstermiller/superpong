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

    def getSize(self) -> (int, int):
        if len(self.nodes) > 0:
            width = max([self.rect.width] + list(n.rect.width for n in self.nodes)) + self.menu.itemHeight*2
            # include room for border top and bottom, menu header, and header padding
            height = (len(self.nodes) + 3)*self.menu.itemHeight
            return (width, height)
        else:
            return (0, 0)

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

    def drawMenu(self, screen: Surface):
        pos = list(self.menu.topleft)
        pos[0] += self.menu.itemHeight

        def advance(positions: float=1):
            pos[1] += int(self.menu.itemHeight*positions)

        advance(0.5)
        screen.blit(self.image, pos)
        advance(2)

        for i, node in enumerate(self.nodes):
            if i == self.selected:
                selectedRect = node.rect.copy()
                selectedRect.topleft = pos
                selectedRect.inflate_ip(self.menu.fontPadding*2, self.menu.fontPadding)
                screen.fill(self.menu.selectColor, selectedRect)
            screen.blit(node.image, pos)
            advance()


class Menu:
    def __init__(self, node: MenuNode, font: Font, fontColor: Color, selectColor: Color,
                 backgroundColor: Color=None, borderColor: Color=None, fadeColor: Color=None):
        self.current = node

        self.font = font
        self.fontColor = fontColor
        self.fontHeight = font.get_height()
        self.fontPadding = int(self.fontHeight/4)
        self.itemHeight = self.fontHeight + self.fontPadding
        self.selectColor = selectColor
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.fadeColor = fadeColor

        self._topleft = (0, 0)
        self._midtop = None
        """:type: (int, int)"""
        self.imageInited = False

        node.init(self)

    @property
    def topleft(self) -> (int, int):
        return self._topleft

    @topleft.setter
    def topleft(self, value):
        self._topleft = value
        if self.imageInited:
            self._midtop = (value[0] + int(self.image.get_size()[0]/2), value[1])
        else:
            self._midtop = None

    @property
    def midtop(self) -> (int, int):
        return self._midtop

    @midtop.setter
    def midtop(self, value):
        self._midtop = value
        if self.imageInited:
            self._topleft = (value[0] - int(self.image.get_size()[0]/2), value[1])

    def handle_event(self, event: EventType) -> bool:
        if event.type != KEYDOWN:
            return False

        self.current.handle_event(event)

    def draw(self, screen: Surface):
        if not self.imageInited:
            self._initImage(screen)

        if self.image:
            drawPos = (0, 0) if self.fadeColor else self.topleft
            screen.blit(self.image, drawPos)
        self.current.drawMenu(screen)

    def _initImage(self, screen: Surface):
        self.imageInited = True

        if self.backgroundColor:
            # search for largest dimensions in tree
            def maxSize(n: MenuNode) -> (int, int):
                sizes = [n.getSize()] + list(maxSize(c) for c in n.nodes)
                return tuple(max(s[d] for s in sizes) for d in range(2))

            node = self.current
            while node.parent:
                node = node.parent

            size = maxSize(node)

            import drawutil
            self.image = drawutil.rect(size, self.backgroundColor, self.fontPadding, self.borderColor)
            # if midtop was set, re-set it to calculate topleft
            if self.midtop:
                self.midtop = self.midtop

        if self.fadeColor:
            fade = Surface(screen.get_size())

            if len(self.fadeColor) > 3:
                fade = fade.convert_alpha()
            else:
                fade = fade.convert()

            fade.fill(self.fadeColor)

            fade.blit(self.image, self.topleft)
            self.image = fade