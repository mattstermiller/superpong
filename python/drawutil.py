import pygame
from pygame import draw, Surface, Color, Rect


def rect(size: (int, int), color: Color, borderSize: int=0, borderColor: Color=None) -> Surface:
    """
    Creates a surface and draws a rectangle, optionally with a border.
    :param size: Pixel size of the rectangle/Surface
    :param color: Color to use
    :param borderSize: Pixel size of each side of the border, if desired
    :param borderColor: Color of the border
    :return: New Surface instance with the specified color and border
    """
    image = Surface(size)

    if len(color) > 3 or len(borderColor) > 3:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if borderSize > 0 and borderColor:
        draw.rect(image, borderColor, Rect((0, 0), size), borderSize*2)

    bgRect = Rect((borderSize, borderSize), tuple((d - borderSize*2 for d in size)))
    draw.rect(image, color, bgRect)

    return image


def colorize(image: Surface, newColor: Color) -> Surface:
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()

    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    return image


def _colorize_test():
    import assets
    pygame.init()
    screen = pygame.display.set_mode((400, 300), pygame.DOUBLEBUF)
    image = assets.load_image('test.png')
    screen.blit(image, (50, 50))

    image2 = colorize(image, (0, 100, 200))
    screen.blit(image2, (150, 50))

    pygame.display.flip()

    pygame.time.wait(2000)
    pygame.quit()


if __name__ == '__main__':
    _colorize_test()
