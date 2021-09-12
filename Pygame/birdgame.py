from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *
FPS = 30
SCREENWIDTH = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE = 100# gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = '/sprites/bird.png'

# list of backgrounds
BACKGROUNDS_LIST = '/sprites/background-day.png'


# list of pipes
PIPES_LIST = '/sprites/pipe-green.png'

def welcomescreen():
	playerx = int(SCREENWIDTH/5)
	playery = int((SCREENHEIGHT - IMAGES['player'].get_height())/2)
	messagey = int(SCREENHEIGHT*0.13)
	messagex = int((SCREENWIDTH - IMAGES['message'].get_width())/2)
	basex = 0
	while True:
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
				SOUNDS['wing'].play()
				return
			SCREEN.blit(IMAGES['background'],(0,0))
			SCREEN.blit(IMAGES['player'],(playerx, playery))
			SCREEN.blit(IMAGES['message'],(messagex, messagey))
			SCREEN.blit(IMAGES['base'],(basex, BASEY))
			pygame.display.update()
			FPSCLOCK.tick(FPS)
def maingame():
	score = 0
	playerx = int(SCREENWIDTH/5)
	playery = int(SCREENHEIGHT/2)
	basex = 0
	
	newPipe1 = getRandomPipe()
	newPipe2 = getRandomPipe()
	upperPipes = [
        {
            'x': SCREENWIDTH + 200,
            'y': newPipe1[0]['y']
        },
        {
            'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2),
            'y': newPipe2[0]['y']
        },
    ]
	lowerPipes = [
    {
    	'x': SCREENWIDTH + 200,
    	'y': newPipe1[1]['y']
    },
    {
    	'x': SCREENWIDTH + 200 + (SCREENWIDTH/2),
    	'y': newPipe2[1]['y']
    }
    ]
	pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
	playerVelY = -9  # player's velocity along Y, default same as playerFlapped
	playerMaxVelY = 10  # max vel along Y, max descend speed
	playerMinVelY = -8  # min vel along Y, max ascend speed
	playerAccY = 1  # players downward accleration
	playerRot = 45  # player's rotation
	playerVelRot = 3  # angular speed
	playerRotThr = 20  # rotation threshold
	playerFlapAcc = -9  # players speed on flapping
	playerFlapped = False
	while True:
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
					if playery > 0:
						playerVelY = playerFlapAcc
						playerFlapped = True
						SOUNDS['wing'].play()
						
		crashTest = checkCrash(playerx, playery, upperPipes, lowerPipes)
		if crashTest:
			return
			
		playerMidPos = playerx + IMAGES['player'].get_width() / 2
		for pipe in upperPipes:
			pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
			if pipeMidPos <= playerMidPos < pipeMidPos + 4:
					score += 1
					SOUNDS['point'].play()
		if playerVelY < playerMaxVelY and not playerFlapped:
			playerVelY += playerAccY
		if playerFlapped:
			playerFlapped = False
			
		playerHeight = IMAGES['player'].get_height()
		playery += min(playerVelY, BASEY - playery - playerHeight)
		for uPipe, lPipe in zip(upperPipes, lowerPipes):
			uPipe['x'] += pipeVelX
			lPipe['x'] += pipeVelX
		if 0 < upperPipes[0]['x'] < 5:
			newPipe = getRandomPipe()
			upperPipes.append(newPipe[0])
			lowerPipes.append(newPipe[1])
		if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
			upperPipes.pop(0)
			lowerPipes.pop(0)
		SCREEN.blit(IMAGES['background'],(0,0))
		for uPipe, lPipe in zip(upperPipes, lowerPipes):
			SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
			SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))
		SCREEN.blit(IMAGES['base'],(basex, BASEY))
			
		scoreDigits = [int(x) for x in list(str(score))]
		totalWidth = 0  # total width of all numbers to be printed
		for digit in scoreDigits:
			totalWidth += IMAGES['numbers'][digit].get_width()
		Xoffset = (SCREENWIDTH - totalWidth) / 2
		for digit in scoreDigits:
			SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
			Xoffset += IMAGES['numbers'][digit].get_width()
		SCREEN.blit(IMAGES['player'],(playerx, playery))
		pygame.display.update()
		FPSCLOCK.tick(FPS)

def checkCrash(playerx,playery, upperPipes, lowerPipes):
	if playery > BASEY - 25 or playery <0:
		SOUNDS['hit'].play()
		return True
	for pipe in upperPipes:
		pipeHeight = IMAGES['pipe'][0].get_height()
		if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < IMAGES['pipe'][0].get_width()):
			SOUNDS['hit'].play()
			return True
	for pipe in lowerPipes:
		if(playery + IMAGES['player'].get_height() > pipe['y'] and abs(playerx - pipe['x']) < IMAGES['pipe'][0].get_width()):
			SOUNDS['hit'].play()
			return True
	return False
            		
    
    
def getRandomPipe():
	gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
	gapY += int(BASEY * 0.2)
	pipeHeight = IMAGES['pipe'][0].get_height()
	pipeX = SCREENWIDTH + 10
	return [
        {
            'x': pipeX,
            'y': gapY - pipeHeight
        },  # upper pipe
        {
            'x': pipeX,
            'y': gapY + PIPEGAPSIZE
        },  # lower pipe
    ]
				
				
			
if __name__ == "__main__" :
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.SCALED | pygame.FULLSCREEN)
    pygame.display.set_caption('Flappy Bird')
    # numbers sprites for score display
    IMAGES['numbers'] = (pygame.image.load('/sprites/0.png').convert_alpha(), pygame.image.load('/sprites/1.png').convert_alpha(), pygame.image.load('/sprites/2.png').convert_alpha(), pygame.image.load('/sprites/3.png').convert_alpha(), pygame.image.load('/sprites/4.png').convert_alpha(), pygame.image.load('/sprites/5.png').convert_alpha(), pygame.image.load('/sprites/6.png').convert_alpha(), pygame.image.load('/sprites/7.png').convert_alpha(), pygame.image.load('/sprites/8.png').convert_alpha(), pygame.image.load('/sprites/9.png').convert_alpha())

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('/sprites/base.png').convert_alpha()
    SOUNDS['die'] = pygame.mixer.Sound('/audio/die.ogg')
    SOUNDS['hit'] = pygame.mixer.Sound('/audio/hit.ogg')
    SOUNDS['point'] = pygame.mixer.Sound('/audio/point.ogg')
    SOUNDS['wing'] = pygame.mixer.Sound('/audio/wing.ogg')
    IMAGES['background']  = pygame.image.load(BACKGROUNDS_LIST).convert()
    IMAGES['player'] = pygame.image.load(PLAYERS_LIST).convert_alpha()
    IMAGES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPES_LIST).convert_alpha(),180),pygame.image.load(PIPES_LIST).convert_alpha())
    while True:
    	welcomescreen()
    	maingame()
