import random, sys, time, math, pygame
from pygame.locals import *

FPS = 40 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# USEFUL COLOR TUPLES
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0,0,0)
YELLOW = (255, 255, 0)
OCEAN_BLUE = (30, 47 * 3 + 50, 74 * 3 + 20)

CAMERASLACK = 90     # how far from the center the frog moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30    # how high the player bounces
STARTSIZE = 50       # how big the player starts off
WINSIZE = 300        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with

NUMfrogS = 20    # number of frogs in the active area
frogMINSPEED = 3 # slowest frog speed
frogMAXSPEED = 7 # fastest frog speed
DIRCHANGEFREQ = 0    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'



"""
This program has three data structures to represent the player, enemy frogs. The data structures are dictionaries with the following keys:

Keys used by all three data structures:
    'x' - the left edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'y' - the top edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'rect' - the pygame.Rect object representing where on the screen the object is located.
Player data structure keys:
    'surface' - the pygame.Surface object that stores the image of the frog which will be drawn to the screen.
    'facing' - either set to LEFT or RIGHT, stores which direction the player is facing.
    'size' - the width and height of the player in pixels. (The width & height are always the same.)
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'health' - an integer showing how many more times the player can be hit by a larger frog before dying.
Enemy frog data structure keys:
    'surface' - the pygame.Surface object that stores the image of the frog which will be drawn to the screen.
    'movex' - how many pixels per frame the frog moves horizontally. A negative integer is moving to the left, a positive to the right.
    'movey' - how many pixels per frame the frog moves vertically. A negative integer is moving up, a positive moving down.
    'width' - the width of the frog's image, in pixels
    'height' - the height of the frog's image, in pixels
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'bouncerate' - how quickly the frog bounces. A lower number means a quicker bounce.
    'bounceheight' - how high (in pixels) the frog bounces
Grass data structure keys:
    'grassImage' - an integer that refers to the index of the pygame.Surface object in BACKGROUNDIMAGES used for this grass object
"""

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_FROG_IMG, R_FROG_IMG, BACKGROUNDIMAGES, BadObjs, GoodObjs

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('images/gameicon.png')) #TOCHANGE
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Licking Frog Man')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_FROG_IMG = pygame.image.load('images/frog.jpg')
    R_FROG_IMG = pygame.transform.flip(L_FROG_IMG, True, False)
    BACKGROUNDIMAGES = []
    BACKGROUNDIMAGES.append(pygame.image.load('images/plain.jpg'))

    #Good Array - These things are recyclable
    L_WATER_BOTTLE_IMG = pygame.image.load("images/waterbottle.jpg")
    R_WATER_BOTTLE_IMG = pygame.transform.flip(L_WATER_BOTTLE_IMG, True, False)
    GoodObjs = [L_WATER_BOTTLE_IMG, R_WATER_BOTTLE_IMG]
    #Bad Array - These things aren't recyclable
    L_TIRES_IMG = pygame.image.load("images/tires.jpg")
    R_TIRES_IMG = pygame.transform.flip(L_TIRES_IMG, True, False)
    BadObjs = [L_TIRES_IMG, R_TIRES_IMG]

    while True:
        runGame()


def runGame():
    # set up variables for the start of a new game
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    winMode = False           # if the player has won

    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, RED)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('OMEGA FROG RECYCLER!', True, GREEN)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, RED)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax and cameray are the top left of where the camera view is
    camerax = 0
    cameray = 0

    Objs = [] # stores all the non-player frog objects
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_FROG_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': MAXHEALTH}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False


    while True: # main game loop
        # Check if we should turn off invulnerability
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # move all the frogs
        for sObj in Objs:
            # move the frog, and adjust for their bounce
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # reset bounce amount

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                if sObj['movex'] > 0: # faces right
                    sObj['surface'] = pygame.transform.scale(R_FROG_IMG, (sObj['width'], sObj['height']))
                else: # faces left
                    sObj['surface'] = pygame.transform.scale(L_FROG_IMG, (sObj['width'], sObj['height']))

        for i in range(len(Objs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, Objs[i]):
                del Objs[i]


        while len(Objs) < NUMfrogS:
            Objs.append(makeNewfrog(camerax, cameray))

        # adjust camerax and cameray if beyond the "camera slack"
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # draw the ocean background
        DISPLAYSURF.fill(OCEAN_BLUE)

        # draw the other frogs
        for sObj in Objs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])


        # draw the player frog
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # draw the health meter
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change player image
                        playerObj['surface'] = pygame.transform.scale(L_FROG_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_FROG_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif winMode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                # stop moving the player's frog
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any frogs
            for i in range(len(Objs)-1, -1, -1):
                sqObj = Objs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):
                    # a player/frog collision has occurred

                    if (sqObj['isgood'] == True): #* sqObj['height'] <= playerObj['size']**2:
                        # player is larger and eats the frog
                        playerObj['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1
                        del Objs[i]

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(L_FROG_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(R_FROG_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True # turn on "win mode"

                    elif not invulnerableMode:
                        # player is smaller and takes damage
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game

        # check if the player has won.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)




def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity():
    speed = random.randint(frogMINSPEED, frogMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewfrog(camerax, cameray):
    sq = {}
    decider = random.randint(1,10)
    generalSize = 10
    sq['width'] = generalSize * 2
    sq['height'] = generalSize * 2
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = getRandomVelocity()
    sq['movey'] = getRandomVelocity()
    sq['bounce'] = 0
    sq['bouncerate'] = 10
    sq['bounceheight'] = 10
    if (decider < 8): #This means we're picking a good object
        #pick random good object
        len_good = len(GoodObjs) // 2
        ran = random.randint(0, len_good-1)
        if sq['movex'] < 0: # frog is facing left
            sq['surface'] = pygame.transform.scale(GoodObjs[ran], (sq['width'], sq['height']))
        else: # frog is facing right
            sq['surface'] = pygame.transform.scale(GoodObjs[ran+1], (sq['width'], sq['height']))
        sq['isgood'] = True
    else: #This means we're picking a bad object
        #pick random bad object
        len_bad = len(BadObjs) // 2
        ran2 = random.randint(0, len_bad-1)

        if sq['movex'] < 0: # frog is facing left
            sq['surface'] = pygame.transform.scale(BadObjs[ran2], (sq['width'], sq['height']))
        else: # frog is facing right
            sq['surface'] = pygame.transform.scale(BadObjs[ran2+1], (sq['width'], sq['height']))
        sq['isgood'] = False

    # generalSize = random.randint(5, 25)
    # multiplier = random.randint(1, 3)
    # sq['width']  = (generalSize + random.randint(0, 10)) * multiplier
    # sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    # sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    # sq['movex'] = getRandomVelocity()
    # sq['movey'] = getRandomVelocity()
    # if sq['movex'] < 0: # frog is facing left
    #     sq['surface'] = pygame.transform.scale(L_FROG_IMG, (sq['width'], sq['height']))
    # else: # frog is facing right
    #     sq['surface'] = pygame.transform.scale(R_FROG_IMG, (sq['width'], sq['height']))
    # sq['bounce'] = 0
    # sq['bouncerate'] = random.randint(10, 18)
    # sq['bounceheight'] = random.randint(10, 50)
    return sq



def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()
