import pygame

class GameSprite(pygame.sprite.Sprite):
    _mainsurf = None

    def __init__(self):
        super().__init__()
        self._mainsurf = pygame.display.get_surface()