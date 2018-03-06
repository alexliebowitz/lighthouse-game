import pygame

class GameSprite(pygame.sprite.Sprite):
    _mainsurf = None
    x = None
    y = None

    def __init__(self):
        super().__init__()
        self._mainsurf = pygame.display.get_surface()

    def setx(self, x):
        self.x = x
        self.rect.x = x

    def sety(self, y):
        self.y = y
        self.rect.y = y

    def incrx(self, xamount):
        self.x += xamount
        self.rect.x = self.x

    def incry(self, yamount):
        self.y += yamount
        self.rect.y = self.y