import pygame
import os
from pygame.locals import *

image_folder = 'images'
sounds_folder = 'sounds'

if not pygame.font:
    print('Warning, fonts disabled!')
if not pygame.mixer:
    print('Warning, sound disabled!')

_imageCache = {}


def load_image(name, color_key=None):
    """
    Load an image file.
    :param name: Name of the image file to load (in assets.images_folder).
    :param color_key: Transparent color (use -1 to use the first pixel)
    :return: Surface instance
    :raise SystemExit: When the image cannot be loaded
    """
    path = os.path.join(image_folder, name)

    if path not in _imageCache:
        try:
            image = pygame.image.load(path)
        except pygame.error as message:
            print('Cannot load image: ', path)
            raise SystemExit(message)

        if name.endswith('.png'):
            image = image.convert_alpha()
        else:
            image = image.convert()

        if color_key is not None:
            if color_key is -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, RLEACCEL)

        _imageCache[path] = image
    else:
        image = _imageCache[path]

    return image


def load_sound(name):
    """
    Load a sound file.
    :param name: Name of the sound file to load (in assets.sounds_folder).
    :return: Sound instance
    :raise SystemExit: When sound cannot be loaded
    """

    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()

    path = os.path.join(sounds_folder, name)
    try:
        sound = pygame.mixer.Sound(path)
    except pygame.error as message:
        print('Cannot load sound: ', path)
        raise SystemExit(message)
    return sound
