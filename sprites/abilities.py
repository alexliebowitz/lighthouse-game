class Shield(pygame.sprite.Sprite):
    _frames = None
    _rocket = None
    radius = None
    done = None

    def __init__(self, rocket):
        super().__init__()

        self._frames = 0
        self.radius = 0
        self._rocket = rocket
        self.done = False

        # We set the self.rect to to match the rocket's rectangle.
        # Height and width don't matter, because as long as we
        # provide a .radius, Pygame will use that for collision
        # detection.
        self.rect = rocket.rect.copy()

        self._circlesurf = pygame.Surface((WIDTH, HEIGHT))
        self._circlesurf.set_alpha(SHIELD_ALPHA)
        self._circlesurf.set_colorkey((0, 0, 0))

    def draw(self):
        self._frames += 1
        if self._frames <= SHIELD_DURATION:
            if self.radius <= SHIELD_MAX:
                self.radius += SHIELD_SPEED
        else:  # We are past the duration, so shrink the field
            self.radius -= SHIELD_SPEED
            if self.radius <= 0:
                self.done = True
                return

        self.rect.centerx = self._rocket.rect.centerx
        self.rect.centery = self._rocket.rect.centery

        self._circlesurf.fill((0, 0, 0))

        pygame.draw.circle(self._circlesurf, SHIELD_COLOR,
                           (self._rocket.rect.centerx, self._rocket.rect.centery), self.radius)
        mainsurf.blit(self._circlesurf, (0, 0))


class Bomb(pygame.sprite.Sprite):
    BLAST_RADIUS = 300
    EXPLOSION_COLOR_1 = (255, 255, 255)
    EXPLOSION_COLOR_2 = (200, 200, 200)
    GROW_RATE = 10
    FUSE = 100

    _frames = None
    _blinker = None
    _frames_since_detonated = None
    _circlesurf = None

    radius = None
    exploding = None
    done = None

    def __init__(self, x, y):
        super().__init__()

        self._frames = 0
        self._blinker = False
        self.radius = 0
        self.exploding = False
        self.done = False
        self._circlesurf = pygame.Surface((WIDTH, HEIGHT))
        self._circlesurf.set_colorkey((0, 0, 0))

        self.image = pygame.image.load("images/bomb.png")
        self.rect = pygame.rect.Rect((x, y), self.image.get_size())

    def _get_alpha(self):
        # ratio_done is how far along we are in the explosion.
        # For example, if we're 50% done, then ratio_done will be 0.5.
        ratio_done = self.radius / self.BLAST_RADIUS

        # Start at 255 (no transparency) and then fade out to 0
        return 255 * (1 - ratio_done)

    def detonate(self):
        self.exploding = True
        self._frames_since_detonated = 0

    def draw(self):
        self._frames += 1
        if self.exploding:
            self._frames_since_detonated += 1

        if self._frames == self.FUSE and not self.exploding:  # At the 100 frame mark, we detonate
            self.detonate()

        if not self.exploding:
            # We haven't exploded yet, so draw the normal bomb
            mainsurf.blit(self.image, self.rect)
        elif self.radius <= self.BLAST_RADIUS:  # Exploding
            self._frames_since_detonated += 1
            if self._frames_since_detonated % 3 == 0:  # Every third frame...
                self._blinker = not self._blinker

            self.radius = self._frames_since_detonated * self.GROW_RATE

            color = self.EXPLOSION_COLOR_1 if self._blinker else self.EXPLOSION_COLOR_2
            self._circlesurf.set_alpha(self._get_alpha())

            # Set the radius based on the number of frames since 100 (so it grows every frame)
            pygame.draw.circle(self._circlesurf, color, (self.rect.centerx, self.rect.centery), self.radius)
            mainsurf.blit(self._circlesurf, (0, 0))
        else:
            # We are past the radius, so we do not draw, and we set this.done to True
            # so the main game loop knows it can remove this from the list of bombs.
            self.done = True

class TimeBomb(Bomb):
    GROW_RATE = 30
    EXPLOSION_COLOR_1 = (100, 100, 255)
    EXPLOSION_COLOR_2 = (50, 50, 255)
    BLAST_RADIUS = 5000
    FUSE = 20

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = pygame.image.load("images/timebomb.png")
        self.rect = pygame.rect.Rect((x, y), self.image.get_size())

    def _get_alpha(self):
        ratio_done = self.radius / self.BLAST_RADIUS

        # Fade out from 255 down based on how far along we are in the explosion.
        # But don't go below 20, so we can always see some blue
        return max(255 * (1 - ratio_done), 20)

    def get_time_scale(self):
        return 0.3
