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
DEVILSPEED = 1.2
MAX_POINTS = 10
MAX_SPEED = 10
BOOST_SPEED = 20
MIN_BOOST = 20
MAX_BOOST = 50
MAIN_COLOR = (255, 0, 0)
STAR_COLOR = (255, 255, 255)

pygame.init()
 
mainfont = pygame.font.SysFont('Helvetica', 25)
 
mainsurf = pygame.display.set_mode((WIDTH, HEIGHT))

rocketimage = pygame.image.load('rocket.png')
cookieimage = pygame.image.load('cookie.png')
devilimage = pygame.image.load('devil.png')

rocketwidth, rocketheight = rocketimage.get_size()
cookiewidth, cookieheight = cookieimage.get_size()
devilwidth, devilheight = devilimage.get_size()

rocketx = WIDTH / 2
rockety = HEIGHT / 2
rocketspeed = 1

boostmode = False
boostleft = MAX_BOOST

devils = []

cookiex = random.randint(0, WIDTH)
cookiey = random.randint(0, HEIGHT)

score = 0

paused = False
gamewon = False
gamelost = False

devilgroup = pygame.sprite.Group()

class Devil(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.rect = pygame.rect.Rect(
            (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
            (devilwidth, devilheight)
        )

        devilgroup.add(self)

    def draw(self):
        mainsurf.blit(devilimage, self)

class StarField(pygame.Surface):
    def __init__(self):
        super().__init__((WIDTH, HEIGHT))

        x = 0
        while x < WIDTH:
            y = 0
            while y < HEIGHT:
                if random.randint(0, 100) == 0:
                    self.set_at((x, y), STAR_COLOR)
                y += 1
            x += 1

# def spawndevil(devils):
#     side = random.randint(0, 3)
#
#     if side == 0:  # Top
#         x = random.randint(0, WIDTH)
#         y = 0
#     elif side == 1:  # Right
#         x = WIDTH
#         y = random.randint(0, HEIGHT)
#     elif side == 2:  # Bottom
#         x = random.randint(0, WIDTH)
#         y = HEIGHT
#     elif side == 3:  # Left
#         x = 0
#         y = random.randint(0, HEIGHT)
#
#     devils.append((x, y))

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
        rockety -= rocketspeed
 
    if keyspressed[K_DOWN]:
        rockety += rocketspeed
 
    if keyspressed[K_LEFT]:
        rocketx -= rocketspeed
 
    if keyspressed[K_RIGHT]:
        rocketx += rocketspeed

    # If the rocket is now past the edge in any direction, move it back to the edge.
    if rocketx < 0:
        rocketx = 0

    if rocketx > WIDTH - rocketwidth:
        rocketx = WIDTH - rocketwidth

    if rockety < 0:
        rockety = 0

    if rockety > HEIGHT - rocketwidth:
        rockety = HEIGHT - rocketwidth
 
    ### Update devil position

    i = 0
    while i < len(devils): # For each devil...
        # Get the current x and y position for this devil
        devil = devils[i]

        oldx = devil.rect.x
        oldy = devil.rect.y

        # Calculate the *new* x and y position for this devil
        if devil.rect.x > rocketx:
            devil.rect.x -= DEVILSPEED
    
        if devil.rect.x < rocketx:
            devil.rect.x += DEVILSPEED
     
        if devil.rect.y > rockety:
            devil.rect.y -= DEVILSPEED
     
        if devil.rect.y < rockety:
            devil.rect.y += DEVILSPEED

        devilgroup.remove(devil)
        collidingdevil = pygame.sprite.spritecollideany(devil, devilgroup)
        devilgroup.add(devil)


        if collidingdevil is not None:
            devil.rect.x = oldx
            devil.rect.y = oldy

        i += 1


    ### We have the new positions for everything. Now, check for collisions and update the game in response

    # Create Pygame rectangle objects for the rocket and cookie. Rectangles are not directly displayed
    # to the screen; they're just used for checking for collisions and other calculations.
    rocket_rect = pygame.Rect((rocketx, rockety), (rocketwidth, rocketheight))
    cookie_rect = pygame.Rect((cookiex, cookiey), (cookiewidth, cookieheight))
 
    # Check if any of the rocket is colliding with any of the devils
    i = 0
    while i < len(devils):
        devil = devils[i]

        if rocket_rect.colliderect(devil.rect):
            gamelost = True
            break
        i += 1
 
    # If the rocket collided with one of the devils, we lost, so we go back to the top of the game
    # loop to display the lose screen.
    if gamelost:
        continue
 
    # Check if the rocket is colliding with the cookie
    if rocket_rect.colliderect(cookie_rect):
        cookiex = random.randint(0, WIDTH)
        cookiey = random.randint(0, HEIGHT)
        score += 1
        devils.append(Devil())

    if score >= MAX_POINTS:
        gamewon = True
    else:
        ### The game state has been updated. Time to render!

        mainsurf.blit(starfield, (0, 0))

        showscore(score)
        showboostbar(boostleft)

        # Render rocket and cookie
        mainsurf.blit(rocketimage, (rocketx, rockety))
        mainsurf.blit(cookieimage, (cookiex, cookiey))
 
        # Render devils
        i = 0
        while i < len(devils):
            devil = devils[i]
            devil.draw()
            i += 1

    pygame.display.update()