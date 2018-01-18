import pygame
import random

from pygame.locals import *

### Initialize constants

WIDTH = 1000
HEIGHT = 800
BOOST_BAR_WIDTH = 150
BOOST_BAR_HEIGHT = 20
BOOST_BAR_COLOR = (0, 255, 0)
BOOST_BAR_COLOR_DEPLETED = (200, 0, 0)
BOOST_BAR_LINE_COLOR = (50, 50, 50)
BACKGROUND_COLOR = (180, 200, 240)
PAUSE_BACKGROUND_COLOR = (255, 255, 255)
FRAMERATE = 60
DEVILSPEED = 3
MAX_POINTS = 10
MAX_SPEED = 10
BOOST_SPEED = 20
MIN_BOOST = 20
MAX_BOOST = 50
MAIN_COLOR = (255, 0, 0)
STAR_COLOR = (255, 255, 255)

pygame.init()
pygame.mixer.init()
 
mainfont = pygame.font.SysFont('Helvetica', 25)

mainsurf = pygame.display.set_mode((WIDTH, HEIGHT))

rocketspeed = 1

boostmode = False
boostleft = MAX_BOOST

devils = []
bombs = []
timebomb = None

score = 0

paused = False
gamewon = False
gamelost = False

devilgroup = pygame.sprite.Group()

winsound = pygame.mixer.Sound("sounds/winscreen.wav")
losesound = pygame.mixer.Sound("sounds/sadtrombone.wav")
levelupsound = pygame.mixer.Sound("sounds/omnomnom.ogg")


class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("images/rocket.png")
        self.rect = pygame.rect.Rect((WIDTH / 2, HEIGHT / 2), self.image.get_size())

    def draw(self):
        mainsurf.blit(self.image, self.rect)

class Devil(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("images/devil.png")

        side = random.randint(0, 3)
        if side == 0:  # Top
            x = random.randint(0, WIDTH)
            y = 0
        elif side == 1:  # Right
            x = WIDTH
            y = random.randint(0, HEIGHT)
        elif side == 2:  # Bottom
            x = random.randint(0, WIDTH)
            y = HEIGHT
        elif side == 3:  # Left
            x = 0
            y = random.randint(0, HEIGHT)

        self.rect = pygame.rect.Rect((x, y), self.image.get_size())

        devilgroup.add(self)

    def draw(self):
        mainsurf.blit(self.image, self.rect)

class BossDevil(Devil):
    def __init__(self):
        super().__init__()

        self._normalimage = pygame.image.load("images/boss.png")
        self._invertedimage = pygame.image.load("images/boss2.png")

        self._framecounter = 0
        self._inverted = False

        self.image = pygame.image.load('images/boss.png')
        self.rect = pygame.rect.Rect((WIDTH / 2, HEIGHT / 2), self.image.get_size())

        devilgroup.add(self)

    def draw(self):
        self._framecounter += 1

        if self._framecounter == 5:
            self._framecounter = 0
            self._inverted = not self._inverted
            if self._inverted:
                self.image = self._invertedimage
            else:
                self.image = self._normalimage

        mainsurf.blit(self.image, self.rect)

class Cookie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("images/cookie.png")
        self.rect = pygame.rect.Rect((random.randint(15, WIDTH - 15), random.randint(15, HEIGHT - 15)), self.image.get_size())

    def draw(self):
        mainsurf.blit(self.image, self.rect)

class Bomb(pygame.sprite.Sprite):
    _frames = None
    _blinker = None
    _frames_since_detonated = None
    radius = None
    exploding = None
    done = None
    _circlesurf = None

    GROW_RATE = 18
    EXPLOSION_COLOR_1 = (255, 255, 255)
    EXPLOSION_COLOR_2 = (200, 200, 200)
    BLAST_RADIUS = 250
    AUTO_DETONATE_FRAMES = 100

    def __init__(self, x, y):
        super().__init__()

        self._frames = 0
        self._blinker = False
        self.radius = 0
        self.exploding = False
        self.done = False

        self.image = pygame.image.load("images/bomb.png")
        self.rect = pygame.rect.Rect((x, y), self.image.get_size())
        self._circlesurf = pygame.Surface((WIDTH, HEIGHT))
        self._circlesurf.set_colorkey((0, 0, 0))

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

        if self._frames == self.AUTO_DETONATE_FRAMES and not self.exploding:  # At the 100 frame mark, we detonate
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

            self.circlesurf.set_alpha(self._get_alpha())

            # Set the radius based on the number of frames since 100 (so it grows every frame)
            pygame.draw.circle(self._circlesurf, color, (self.rect.centerx, self.rect.centery), self.radius)
            mainsurf.blit(self._circlesurf, (0, 0))
        else:
            # We are past the radius, so we do not draw, and we set this.done to True
            # so the main game loop knows it can remove this from the list of bombs.
            self.done = True

class TimeBomb(Bomb):
    GROW_RATE = 30
    EXPLOSION_COLOR_1 = (100, 100, 255, 128)
    EXPLOSION_COLOR_2 = (50, 50, 255, 128)
    BLAST_RADIUS = 5000
    AUTO_DETONATE_FRAMES = 20

    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = pygame.image.load("images/timebomb.png")
        self.rect = pygame.rect.Rect((x, y), self.image.get_size())

    def _get_alpha(self):
        ratio_done = self.radius / self.BLAST_RADIUS

        # Fade out from 255 down based on how far along we are in the explosion.
        # But don't go below 20, so we can always see some blue
        return max(255 * (1 - ratio_done), 20)


    def getspeedmodifier(self):
        # Used by the main game loop to find out how much the world
        # should be slowed down. Returns a number from 0 to 1.
        return 0.3


class StarField(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.rect = pygame.rect.Rect((0, 0), self.image.get_size())

        y = 0
        while y < HEIGHT:
            x = 0
            while x < WIDTH:
                if random.randint(0, 100) == 0:
                    startype = random.choice(['white', 'red', 'blue'])
                    if startype == 'white':
                        color = (255, 255, 255)
                    elif startype == 'red':
                        color = (random.randint(150, 255), 50, 50)
                    elif startype == 'blue':
                        color = (50, 50, random.randint(150, 255))

                    self.image.set_at((x, y), color)
                x += 1
            y += 1

    def draw(self):
        mainsurf.blit(self.image, self.rect)

def winscreen():
    mainsurf.fill(BACKGROUND_COLOR)
 
    textsurf = mainfont.render('YOU WON', True, MAIN_COLOR)
 
    mainsurf.blit(textsurf, (WIDTH / 2, HEIGHT / 2))
 
def losescreen():
    mainsurf.fill(BACKGROUND_COLOR)
 
    textsurf = mainfont.render('YOU LOST', True, MAIN_COLOR)
 
    mainsurf.blit(textsurf, (WIDTH / 2, HEIGHT / 2))

def pausescreen():
    mainsurf.fill(PAUSE_BACKGROUND_COLOR)

    textsurf = mainfont.render("PAUSED", True, MAIN_COLOR)

    mainsurf.blit(textsurf, (WIDTH / 2, HEIGHT / 2))
 
def showscore(score):
    textsurf = mainfont.render(str(score), True, MAIN_COLOR)
    mainsurf.blit(textsurf, (WIDTH - 50, 50))

def showboostbar(boostleft):
    width = (boostleft / MAX_BOOST) * BOOST_BAR_WIDTH

    if boostleft < MIN_BOOST:
        color = BOOST_BAR_COLOR_DEPLETED
    else:
        color = BOOST_BAR_COLOR

    # The x position of the bar is the width of the screen, minus the width of the bar
    # (so it doesn't go off the screen), minus another 30px so it's not right up
    # against the edge of the screen.
    barx = WIDTH - BOOST_BAR_WIDTH - 30

    # y position is 20px (just a little bit of padding so it's not right at the top)
    bary = 20

    # The width of the bar is the percentage of boost that we have left, times the width
    # of the full bar. So if we're at 50% boost and the full bar is 150 pixels, then
    # we display a bar 75 pixels wide.
    barwidth = (boostleft / MAX_BOOST) * BOOST_BAR_WIDTH

    # The height is just a constant
    barheight = BOOST_BAR_HEIGHT

    # Time to draw the bar!
    pygame.draw.rect(mainsurf, color, (barx, bary, barwidth, barheight))

    # Now, let's make the line that marks the minimum boost level

    # To compute the x position for the minimum boost line, we take 3 steps:
    #   - First, we divide the minimum boost over the maximum boost, to find out
    #     how far along the bar we should draw the line (as a ratio). For example,
    #     if MIN_BOOST is 20 and MAX_BOOST is 100, then the ratio would be 0.2.
    #   - Next, we multiply this ratio by the width of the bar to get the actual
    #     number of pixels.
    #   - Finally, we add the x position of the bar to push the whole thing to the
    #     right so it lines up with the bar.
    linex = ((MIN_BOOST / MAX_BOOST) * BOOST_BAR_WIDTH) + barx

    # Line y position is the same as bar
    liney = bary

    # Line is 2 pixels wide
    linewidth = 2

    # Line is same height as bar
    lineheight = barheight

    pygame.draw.rect(mainsurf, BOOST_BAR_LINE_COLOR, (linex, liney, linewidth, lineheight))

starfield = StarField()

rocket = Rocket()
cookie = Cookie()

# Create first devil
devils.append(Devil())
while True:
    event = pygame.event.poll()     
 
    if event.type == QUIT:
        exit()
 
    if gamewon:
        winscreen()
        pygame.display.update()
        continue
 
    if gamelost:
        losescreen()
        pygame.display.update()
        continue

    if event.type == KEYUP and event.key == K_ESCAPE:  # If the player just pressed escape...
        paused = not paused  # Flip paused state

    # If the game is paused, display the pause screen and skip everything else
    if paused:
        pausescreen()
        pygame.display.update()
        continue

    keyspressed = pygame.key.get_pressed()

    ### Update rocket speed

    # If the player pressed "b" and we have enough boost to start, then go into boost mode
    if event.type == KEYDOWN and event.key == K_b and boostleft > MIN_BOOST:
        boostmode = True
        rocketspeed = 20

    if event.type == KEYUP and event.key == K_b:  # Boost mode over
        boostmode = False
        rocketspeed = 1

    if boostmode:
        # We're in boost mode

        boostleft -= 1  # Deplete the boost counter
        if boostleft <= 0:
            boostmode = False
            rocketspeed = 1
    else:
        # We're not in boost mode

        # Replenish boost counter
        if boostleft <= MAX_BOOST:
            boostleft += 0.25

        # If space is held down, increase rocket speed (but don't let the speed go over the max)
        if keyspressed[K_SPACE]:
            rocketspeed += .25
            if rocketspeed > MAX_SPEED:
                rocketspeed = MAX_SPEED

        # If shift is held down, decrease rocket speed (but don't let the speed go under 0)
        if keyspressed[K_LSHIFT] or keyspressed[K_RSHIFT]:
            rocketspeed -= 1
            if rocketspeed < 0:
                rocketspeed = .1

    ### Update rocket position using the speed we just calculated

    if keyspressed[K_UP]:
        rocket.rect.y -= rocketspeed
 
    if keyspressed[K_DOWN]:
        rocket.rect.y += rocketspeed
 
    if keyspressed[K_LEFT]:
        rocket.rect.x -= rocketspeed
 
    if keyspressed[K_RIGHT]:
        rocket.rect.x += rocketspeed

    # If the rocket is now past the edge in any direction, move it back to the edge.
    if rocket.rect.x < 0:
        rocket.rect.x = 0

    if rocket.rect.x > WIDTH - rocket.rect.width:
        rocket.rect.x = WIDTH - rocket.rect.width

    if rocket.rect.y < 0:
        rocket.rect.y = 0

    if rocket.rect.y > HEIGHT - rocket.rect.height:
        rocket.rect.y = HEIGHT - rocket.rect.height
 
    ### Update devil positions

    # If there is a time bomb and it's exploding, get the speed modifier
    # so we can slow down devils that are colliding with it.
    if timebomb is not None and timebomb.exploding:
        speedmodifier = timebomb.getspeedmodifier()

    i = 0
    while i < len(devils): # For each devil...
        # Get the current x and y position for this devil
        devil = devils[i]

        if timebomb is not None and timebomb.exploding and pygame.sprite.collide_circle(timebomb, rocket):
            # There is time bomb exploding and this devil is colliding with it, so slow down the devil
            # by multiplying the speed by the modifier returned (for example, if the speed modifier is
            # 0.5, we go half speed)
            speed = DEVILSPEED * speedmodifier
        else:
            # This devil is not colliding with an exploding time bomb, so use the normal speed.
            speed = DEVILSPEED

        oldx = devil.rect.x
        oldy = devil.rect.y

        # Calculate the *new* x and y position for this devil
        if devil.rect.x > rocket.rect.x:
            devil.rect.x -= speed
    
        if devil.rect.x < rocket.rect.x:
            devil.rect.x += speed
     
        if devil.rect.y > rocket.rect.y:
            devil.rect.y -= speed
     
        if devil.rect.y < rocket.rect.y:
            devil.rect.y += speed

        devilgroup.remove(devil)
        collidingdevil = pygame.sprite.spritecollideany(devil, devilgroup)
        devilgroup.add(devil)


        if collidingdevil is not None:
            devil.rect.x = oldx
            devil.rect.y = oldy

        i += 1

    if event.type == KEYDOWN and event.key == K_d:
        for bomb in bombs:
            bomb.detonate()

    ### We have the new positions for everything. Now, check for collisions and update the game in response

    # Check if the rocket is colliding with any of the devils. If so, we lost
    i = 0
    while i < len(devils):
        devil = devils[i]

        if rocket.rect.colliderect(devil.rect):
            gamelost = True
            break
        i += 1

    if gamelost:
        losesound.play()
        continue

    # Check for collisions with bombs.
    for bomb in bombs:
        if bomb.exploding and pygame.sprite.collide_circle(bomb, rocket):
            # If the rocket is colliding with an exploding bomb, we lose
            gamelost = True
            continue

        for devil in list(devils):
            # If a devil is colliding with an exploding bomb, it goes bye-bye
            if bomb.exploding and pygame.sprite.collide_circle(bomb, devil):
                devils.remove(devil)
                devilgroup.remove(devil)

    if event.type == KEYDOWN and event.key == K_d:
        for bomb in bombs:
            bomb.detonate()


    if gamelost:
        losesound.play()
        continue
 
    # Check if the rocket is colliding with the cookie
    if rocket.rect.colliderect(cookie.rect):
        score += 1

        if score > MAX_POINTS:  # We won
            gamewon = True
            winsound.play()
            continue
        else:
            cookie = Cookie()
            if score == MAX_POINTS:  # Final level
                devilgroup.empty()
                devils = [BossDevil()]
            else:
                for i in range(score):
                    devils.append(Devil())
            levelupsound.play()

    if event.type == KEYUP and event.key == K_RETURN:  # Drop a bomb
        bombs.append(Bomb(rocket.rect.x, rocket.rect.y))

    # Clear out bombs that have finished detonating
    for bomb in list(bombs):
        if bomb.done:
            bombs.remove(bomb)

    if timebomb is not None and timebomb.done:
        timebomb = None

    if event.type == KEYDOWN and event.key == K_t and timebomb is None:  # Drop a time bomb
        timebomb = TimeBomb(rocket.rect.x, rocket.rect.y)



    ### The game state has been updated. Time to render!

    starfield.draw()

    showscore(score)
    showboostbar(boostleft)

    # Render rocket and cookie
    rocket.draw()
    cookie.draw()

    # Render devils
    i = 0
    while i < len(devils):
        devil = devils[i]
        devil.draw()
        i += 1

    # Render bombs
    for bomb in bombs:
        bomb.draw()

    # Render time bomb
    if timebomb is not None:
        timebomb.draw()

    rocket.draw()

    pygame.display.update()
