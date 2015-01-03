from pygame import draw, Surface, Color, Rect


def rect(size: (int, int), color: Color, borderSize: int=0, borderColor: Color=None) -> Surface:
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
