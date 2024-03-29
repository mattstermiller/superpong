from pygame.locals import *
from pygame.constants import *
from pygame import Surface
from pygame.event import EventType
from pygame.font import Font
import pygame
import pygame.gfxdraw
from config import Config


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
        self.imageDisabled = None
        """:type: Surface"""
        self.rect = None
        """:type: Rect"""

        self.nodes = []
        self.selected = 0
        self.disabled = False
        self.visibleIndex = 0

    def init(self, menu: Menu):
        self.menu = menu
        self.image = menu.font.render(self.text, True, menu.foreColor)
        self.rect = self.image.get_rect()

        self.imageDisabled = self.image.copy()
        self.imageDisabled.fill((255, 255, 255, 90), None, BLEND_RGBA_MULT)

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
            visibleNodes = min(len(self.nodes), self.menu.visibleItems)
            height = (visibleNodes + 4)*self.menu.itemHeight
            return width, height
        else:
            return 0, 0

    def handle_event(self, event: EventType) -> bool:
        if event.key == K_UP:
            if self.selected > 0:
                self.selected -= 1
                if self.selected < self.visibleIndex:
                    self.visibleIndex = self.selected
            return True
        elif event.key == K_PAGEUP:
            self.selected = max(self.selected - self.menu.visibleItems, 0)
            self.visibleIndex = max(self.visibleIndex - self.menu.visibleItems, 0)
            return True
        elif event.key == K_HOME:
            self.selected = 0
            self.visibleIndex = self.selected
            return True
        elif event.key == K_DOWN:
            if self.selected < len(self.nodes) - 1:
                self.selected += 1
            if self.selected >= self.visibleIndex + self.menu.visibleItems:
                self.visibleIndex += 1
            return True
        elif event.key == K_PAGEDOWN:
            self.selected = min(self.selected + self.menu.visibleItems, len(self.nodes) - 1)
            self.visibleIndex = min(self.visibleIndex + self.menu.visibleItems, len(self.nodes) - self.menu.visibleItems)
            return True
        elif event.key == K_END:
            self.selected = len(self.nodes) - 1
            self.visibleIndex = min(self.selected, len(self.nodes) - self.menu.visibleItems)
            return True
        elif event.key == K_RETURN:
            self.nodes[self.selected].invoke()
            return True
        elif event.key == K_ESCAPE:
            if self.parent:
                self.menu.current = self.parent
            self.visibleIndex = 0
            return True

        for node in self.nodes:
            if event.key == node.key:
                node.invoke()
                return True

        return False

    def invoke(self):
        if not self.disabled:
            if len(self.nodes) > 0:
                self.selected = 0
                self.menu.current = self
            elif self.callback:
                self.callback()

    def draw(self, screen: Surface, pos: (int, int)):
        if self.disabled:
            screen.blit(self.imageDisabled, pos)
        else:
            screen.blit(self.image, pos)

    def drawMenu(self, screen: Surface):
        pos = list(self.menu.topleft)
        pos[0] += self.menu.itemHeight

        def advance(positions: float=1):
            pos[1] += int(self.menu.itemHeight*positions)

        advance()
        screen.blit(self.image, pos)
        advance()

        if self.visibleIndex > 0:
            screen.blit(self.menu.arrowUp, pos)
        advance()

        visibleEnd = self.visibleIndex + self.menu.visibleItems
        for i, node in list(enumerate(self.nodes))[self.visibleIndex:visibleEnd]:
            if i == self.selected:
                selectedRect = node.rect.copy()
                selectedRect.topleft = pos
                selectedRect.inflate_ip(self.menu.fontPadding*2, self.menu.fontPadding)
                screen.fill(self.menu.selectColor, selectedRect)
            node.draw(screen, pos)
            advance()

        if len(self.nodes) > visibleEnd:
            screen.blit(self.menu.arrowDown, pos)


class CheckMenuNode(MenuNode):
    def __init__(self, text: str, callback=None, key: int=None):
        MenuNode.__init__(self, text, callback, key)
        self.checked = False
        self.checkRect = None

    def init(self, menu: Menu):
        MenuNode.init(self, menu)

        self.rect.width += self.menu.fontHeight - self.menu.fontPadding
        image = Surface(self.rect.size).convert_alpha()
        image.fill([0]*4)
        image.blit(self.image, (self.menu.fontHeight - self.menu.fontPadding, 0))
        self.image = image

        box = Rect((0, 0), [self.menu.fontHeight]*2)
        box.inflate_ip([-self.menu.fontPadding*2]*2)
        box.x = 0
        image.fill(self.menu.foreColor, box)
        self.checkRect = box.inflate([-self.menu.fontPadding]*2)

    def invoke(self):
        if not self.disabled:
            self.checked = not self.checked
        MenuNode.invoke(self)

    def draw(self, screen: Surface, pos: (int, int)):
        MenuNode.draw(self, screen, pos)
        if self.checked:
            screen.fill(self.menu.selectColor, self.checkRect.move(pos))


class RadioMenuNode(CheckMenuNode):
    def __init__(self, text: str, callback=None, key: int=None):
        CheckMenuNode.__init__(self, text, callback, key)

    def invoke(self):
        if not self.disabled:
            self.checked = True
            for node in self.parent.nodes:
                if node is not self:
                    node.checked = False
        MenuNode.invoke(self)


class KeyBindMenuNode(MenuNode):
    def __init__(self, bindingName: str, configName: str, config: Config, callback=None, key: int=None):
        MenuNode.__init__(self, bindingName + ': <press any key>', callback, key)

        self.bindingName = bindingName
        self.configName = configName
        self.config = config

        self.displayImage = None
        self.listenImage = None

    def init(self, menu: Menu):
        MenuNode.init(self, menu)
        self.listenImage = self.image

        def bind(key):
            text = '{}: {}'.format(self.bindingName, pygame.key.name(key))
            self.displayImage = self.menu.font.render(text, True, self.menu.foreColor)
            self.image = self.displayImage

        self.config.subscribe(self.configName, bind)

    def invoke(self):
        self.image = self.listenImage
        self.parent.handle_event = self.listen

    def listen(self, event: EventType) -> bool:
        if event.key != K_ESCAPE:
            self.config[self.configName] = event.key
            self.config.save()
            if self.callback:
                self.callback(event.key)
        else:
            self.image = self.displayImage

        del self.parent.handle_event
        return True


class Menu:
    KEY_REPEAT_START = 0.35
    KEY_REPEAT_INTERVAL = 0.05

    def __init__(self, node: MenuNode, font: Font, foreColor: Color, selectColor: Color, backgroundColor: Color=None,
                 borderColor: Color=None, fadeColor: Color=None, visibleItems: int=5):
        self.current = node

        self.font = font
        self.foreColor = foreColor
        self.fontHeight = font.get_height()
        self.fontPadding = int(self.fontHeight/4)
        self.itemHeight = self.fontHeight + self.fontPadding
        self.selectColor = selectColor
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.fadeColor = fadeColor
        self.visibleItems = visibleItems

        self.image = None
        """:type: Surface"""
        self.imageFade = None
        """:type: Surface"""
        self._rect = Rect(0, 0, 0, 0)
        self._usingMidtop = False
        self.imageInited = False

        self.repeatEvent = None
        """:type: EventType"""
        self.repeatTimeout = None
        """:type: float"""

        # render scroll arrows
        arrowSize = int(self.itemHeight/3)

        def drawArrow(isDown: bool) -> Surface:
            image = Surface((arrowSize + 1, self.itemHeight)).convert_alpha()
            image.fill((0, 0, 0, 0))

            if isDown:
                sideY = 0
                pointY = sideY + arrowSize
            else:
                sideY = self.itemHeight - self.fontPadding
                pointY = sideY - arrowSize

            pygame.gfxdraw.filled_trigon(image, 0, sideY, arrowSize-1, sideY, int(arrowSize/2), pointY, foreColor)
            return image

        self.arrowUp = drawArrow(False)
        self.arrowDown = drawArrow(True)

        node.init(self)

    @property
    def root(self) -> MenuNode:
        node = self.current
        while node.parent:
            node = node.parent
        return node

    @property
    def topleft(self) -> (int, int):
        return self._rect.topleft

    @topleft.setter
    def topleft(self, value):
        self._rect.topleft = value
        self._usingMidtop = False

    @property
    def midtop(self) -> (int, int):
        return self._rect.midtop

    @midtop.setter
    def midtop(self, value):
        self._rect.midtop = value
        self._usingMidtop = True

    def initImage(self, screenSize: (int, int)):
        self.imageInited = True

        if self.backgroundColor:
            # search for largest dimensions in tree
            def maxSize(n: MenuNode) -> (int, int):
                sizes = [n.getSize()] + list(maxSize(c) for c in n.nodes)
                return tuple(max(s[d] for s in sizes) for d in range(2))

            size = maxSize(self.root)

            import drawutil
            self.image = drawutil.rect(size, self.backgroundColor, self.fontPadding, self.borderColor)
            if self._usingMidtop:
                oldMidtop = self._rect.midtop
            self._rect.size = self.image.get_size()
            if self._usingMidtop:
                self._rect.midtop = oldMidtop

        if self.fadeColor:
            self.imageFade = Surface(screenSize)

            if len(self.fadeColor) > 3:
                self.imageFade = self.imageFade.convert_alpha()
            else:
                self.imageFade = self.imageFade.convert()

            self.imageFade.fill(self.fadeColor)

    def reset(self):
        self.current = self.root
        self.current.selected = 0

    def handle_event(self, event: EventType) -> bool:
        if event.type == KEYDOWN:
            self.repeatEvent = event
            self.repeatTimeout = self.KEY_REPEAT_START
            return self.current.handle_event(event)
        elif event.type == KEYUP:
            self.repeatEvent = None
            self.repeatTimeout = None

        return False

    def update(self, delta: float):
        if self.repeatTimeout is not None:
            self.repeatTimeout -= delta
            if self.repeatTimeout <= 0:
                self.repeatTimeout = self.KEY_REPEAT_INTERVAL
                self.current.handle_event(self.repeatEvent)

    def draw(self, screen: Surface):
        if not self.imageInited:
            self.initImage(screen.get_size())

        if self.imageFade:
            screen.blit(self.imageFade, (0, 0))
        if self.image:
            screen.blit(self.image, self._rect.topleft)
        self.current.drawMenu(screen)
