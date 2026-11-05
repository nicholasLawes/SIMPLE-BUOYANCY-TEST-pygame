import pygame
from sys import exit
from math import sqrt
from pygame.locals import *


pygame.init()


screenSize = [1280, 720]
screen = pygame.display.set_mode((screenSize[0], screenSize[1]))
pygame.display.set_caption("hello buoyancy")
clock = pygame.time.Clock()
getTicksLastFrame = pygame.time.get_ticks()

#on-screen STUFF
# // PLAYER
playerSurf = pygame.Surface((150, 150))
playerSurf.fill((255, 0, 0))
playerRect = playerSurf.get_rect(center = (screenSize[0] // 2, screenSize[1] // 2))

# // MOUSE STUFF
mouseSpeed = 0
lastMousePos = 0

getTicksLastFrame = 0

# // GROUND
groundSurf = pygame.Surface((75, 75))
groundSurf.fill((255, 255, 255))
groundRect = groundSurf.get_rect(center = (screenSize[0] // 2, (screenSize[1] // 2) + 500))

# // WATER
waterSurf = pygame.Surface((screenSize[0], 250))
waterSurf.fill((0, 155, 255))
waterRect = waterSurf.get_rect(center = (screenSize[0] // 2, (screenSize[1] // 2) + 250))


#Classes
class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y


#INPUTS
horizontal = 0
verticle = 0
inputAxis = Vector2(horizontal, verticle)
inputMagnitude = 0


#PHYSICS
velocityX = 0
velocityY = 0
boundaryVelocityX = 0
boundaryVelocityY = 0
gravity = 9.81#0
buoyancy = 9.81
buoyancyForce = 0.075

bounceSpeed = 25
playerMass = 60
playerDensity = playerMass / (150*150)
fluidVolume = 0
playerBounciness = 2
speed = 5
accel = 0.075
decel = 0.0275


#Functions
def DoQuitPygame():
    pygame.display.quit()
    pygame.quit()
    exit()


def lerp(a, z, t):
        return a * (1 - t) + z * t



def DoInput():
    for event in pygame.event.get():
        if event == pygame.QUIT:
            DoQuitPygame()


    pressedKeys = pygame.key.get_pressed()

    if pressedKeys[K_ESCAPE]:
        DoQuitPygame()


    if pressedKeys[K_w]:
        inputAxis.y = lerp(inputAxis.y, -1, accel)
    elif pressedKeys[K_s]:
        inputAxis.y = lerp(inputAxis.y, 1, accel)
    else:
        inputAxis.y = lerp(inputAxis.y, 0, accel)
    
    if pressedKeys[K_d]:
        inputAxis.x = lerp(inputAxis.x, 1, accel)
    elif pressedKeys[K_a]:
        inputAxis.x = lerp(inputAxis.x, -1, accel)
    else:
        inputAxis.x = lerp(inputAxis.x, 0, accel)

    
    magneticFlag = False
    if pressedKeys[K_m] and magneticFlag == False:
        playerMagnetic = True
    elif pressedKeys[K_m] and magneticFlag:
        playerMagnetic = True

    inputMagnitude = sqrt(inputAxis.x ** 2 + inputAxis.y ** 2)
    if inputMagnitude > 1:
        inputAxis.x /= inputMagnitude
        inputAxis.y /= inputMagnitude


def DoInputMove():
    velocity = Vector2(inputAxis.x * speed, inputAxis.y * speed)

    #playerRect.move_ip(velocity.x, velocity.y)
    return velocity


def DoCollisions(mouseSpeed):
    global velocityX
    global velocityY
    global boundaryVelocityX
    global boundaryVelocityY
    global gravity
    global buoyancy
    global playerDensity
    global fluidVolume


    if playerRect.colliderect(groundRect) and (playerRect.centerx > groundRect.right) and (playerRect.top < groundRect.bottom) and (playerRect.bottom > groundRect.top):
        playerRect.left = groundRect.right
        velocityX = 1
    elif playerRect.colliderect(groundRect) and (playerRect.centerx < groundRect.left) and (playerRect.top < groundRect.bottom) and (playerRect.bottom > groundRect.top):
        playerRect.right = groundRect.left
        velocityX = -1
    elif playerRect.colliderect(groundRect) and (playerRect.centery < groundRect.bottom) and (playerRect.centerx < groundRect.right) and (playerRect.centerx > groundRect.left):
        playerRect.bottom = groundRect.top
        velocityY = -1
    elif playerRect.colliderect(groundRect) and (playerRect.centery > groundRect.top) and (playerRect.centerx < groundRect.right) and (playerRect.centerx > groundRect.left):
        playerRect.top = groundRect.bottom
        velocityY = 1

    if playerRect.left < 0:
        boundaryVelocityX = 1
    if playerRect.right > screenSize[0]:
        boundaryVelocityX = -1

##    if playerRect.bottom > screenSize[1]:
##        boundaryVelocityY = -1
        
    if playerRect.top < 0:
        boundaryVelocityY = 1

    velocityX = lerp(velocityX, 0, decel)
    velocityY = lerp(velocityY, 0, decel)
    boundaryVelocityX = lerp(boundaryVelocityX, 0, decel)
    boundaryVelocityY = lerp(boundaryVelocityY, 0, decel)

    if playerRect.colliderect(waterRect) or playerRect.bottom > screenSize[1]:
        fluidVolume = screenSize[0] * 350
        # YOU NEED TO DO A WHOLE REWRITE buoyancy = lerp(buoyancy, fluidVolume * gravity * playerDensity, -gravity)
        buoyancy = lerp(buoyancy, -gravity - 3, buoyancyForce)
    else:
        buoyancy = 0


    #playerRect.move_ip(velocityX * smashSpeed * mouseSpeed, velocityY * smashSpeed + gravity * mouseSpeed)
    #mouseSpeed *= 180
    #print(mouseSpeed)
    return Vector2((velocityX + boundaryVelocityX) * bounceSpeed * playerBounciness, ((velocityY + boundaryVelocityY) * bounceSpeed * playerBounciness) + (gravity + buoyancy))

def DoMouse():
    global getTicksLastFrame
    mousePos = pygame.mouse.get_pos()
    groundRect.center = mousePos
    lastMousePos = mousePos
    distance = (mousePos[0] - lastMousePos[0]) + (mousePos[1] - lastMousePos[1])
    t = pygame.time.get_ticks()
    deltatime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t
    speed = (distance / t) * deltatime
    #print(speed)
    return speed

def DoMove():
    DoInput()
    mouseSpeed = DoMouse()
    collisionMovement = DoCollisions(mouseSpeed)
    inputMovement = DoInputMove()

    playerRect.move_ip(inputMovement.x + collisionMovement.x, inputMovement.y + collisionMovement.y)


while True:
    DoMove()

    screen.fill((0, 0, 0))
    screen.blit(waterSurf, waterRect)
    screen.blit(playerSurf, playerRect)
    screen.blit(groundSurf, groundRect)
    

    pygame.display.update()
    clock.tick(50)
