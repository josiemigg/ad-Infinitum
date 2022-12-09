
from cmu_112_graphics import *
import random
import math
import time

import module_manager
module_manager.review()

from pydub import*
import simpleaudio as sa
import numpy as np


### IMPORTANT!!! IF SONGS ARE NOT IN THE PROJECT FOLDER, SET songsEnabled FALSE!!! ###
### IF SONGS ARE DOWNLOADED AND IN THE FOLDER, SET songsEnabled TO TRUE!!! ###
songsEnabled = True 

### If your program runs poorly in the gamemode, set this to False to boost performance. Turns off the synthwave image. ###
bgImageEnabled = True


### COLORS ###

orange = '#FF6C11'
yellow = '#F9C80E'

salmon = '#FF3864'
pinkSalmon = '#FD3777'
redSalmon = '#FD1D53'

darkIndigo = '#261447'
abyss = '#0D0221'
dullAbyss = '#241734'

fuschia1 = '#F706CF'
fuschia2 = '#F6019D'
fuschia3 = '#D40078'

purple1 = '#920075'
purple2 = '#650D89'
purple3 = '#791E94'
purple4 = '#541388' 

cyan = '#55EFFF'
blue = '#023788'
black = '#000000'

##############



class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xVel = 0
        self.yVel = 0
        self.jumpStrength = 5

        
        
        self.r = 10
        self.fill = black
        self.outline = cyan
        self.gravityStrength = 0.4 # the lower the number, the lower the gravity, and the higher the player can jump!
        self.gravityMax = -7.5
        self.xFriction = 0.25
        self.groundLvl = 600 # defines ground level. Temporary.

        self.canJump = True
        self.tryLeft = False
        self.tryRight = False

        self.dirFacing = 'Right'

        
    
    def updatePos(self):
        self.x += self.xVel
        self.y -= self.yVel
        if self.xVel > 0: 
            self.dirFacing = 'Right'
            self.tryLeft = False
        elif self.xVel < 0:
            self.dirFacing = 'Left'
            self.tryRight = False
        if self.x < 0:
            self.x = 0
            self.xVel = 0

        if self.canJump:
            self.outline = cyan
        elif self.canJump == False:
            self.outline = orange


    def jump(self): # need to fix this so that if the player is not actively
        # colliding down, cannot jump
        # or if the player has not collided in the past 0.1 seconds, cant jump
        if self.canJump == True:
            self.yVel = self.jumpStrength
            self.canJump = False

    def die(self, x, y): # this occurs when the player touches a hazard block
        # basically reinitialize the player, eventually to the spawn point of that chunk
        self.xVel = 0
        self.yVel = 0
        self.x , self.y = x, y
        self.canJump = False
        self.tryRight, self.tryLeft = False, False


    def gravity(self):

        if self.yVel <= self.gravityMax:
            self.yVel = self.gravityMax
        # if self.position not touching terrain: apply gravity
        if self.y < (self.groundLvl): # temporarily the ground level
            # if y is above the ground:
            self.yVel -= self.gravityStrength
        elif self.y > self.groundLvl: # if y is below the ground
            self.y = self.groundLvl
            self.yVel = 0
            self.canJump = True
        elif self.y == self.groundLvl: # if on the hardcoded ground
            self.canJump = True
        else:
            self.yVel = 0
            

        # also applies to xVel: if key not being held down, slow the player
        if abs(self.xVel) > 0.1:
            if self.xVel < 0:
                self.xVel += self.xFriction
            elif self.xVel > 0:
                self.xVel -= self.xFriction
        elif abs(self.xVel) <= self.xFriction:
            self.xVel = 0
    
    def collide(self, direction, edgePos):

        if direction == 'Left':
            self.x = edgePos + self.r
            self.xVel = 0
            if self.yVel <= 0 and self.tryLeft == False:
                self.canJump = True
            elif self.yVel > 0:
                self.tryLeft = True



        if direction == 'Right':
            self.x = edgePos - self.r
            self.xVel = 0
            if self.yVel <= 0 and self.tryRight == False:
                self.canJump = True
            elif self.yVel > 0:
                self.tryRight = True

        if direction == "Down":
            self.y = edgePos - self.r
            self.yVel = 0
            self.canJump = True # works like transformice
            self.tryLeft = False
            self.tryRight = False
            # curTime = time.time()
            # if (time.time() - curTime) > 0.01:
            #     self.canJump = False

        if direction == "Up":
            self.y = edgePos + self.r
            self.yVel = 0
    
    def completeChunk(self):
        self.y = self.groundLvl
        self.yVel = 0
        self.canJump = False

###########

class Terrain(object):
    def __init__(self, row, col, type): # row, col --> position
        # type --> if it is a hazard (eg spikes, kill player if player touches)
        # or if it is a typical piece of terrain player can stand on and be okay
        self.row = row
        self.col = col
        self.type = type
        if self.type == 'hazard':
            randColors = [fuschia1, fuschia2, fuschia3, salmon, pinkSalmon, redSalmon]
            randomInt = random.randrange(len(randColors))
            self.fill = 'black'
            self.outline = randColors[randomInt]
        elif self.type == 'terrain':
            randColors = ['#4a11a6', '#4e11a6', '#2f11a6', '#1311a6']
            randomInt = random.randrange(len(randColors))
            self.fill = 'black'
            self.outline = randColors[randomInt]
            
    
    def __eq__(self, other): # test if there is an object here
        return (self.row == other.row and self.col == other.col)



###############################################################################

def distanceFormula(x0, y0, x1, y1):
    return (((x0-x1)**2 + (y0-y1)**2)**0.5)

def checkTouchWall(app):
    for block in app.terrain: # code something so that you estimate
        # player's position in terms of rows and cols. If player 
        # row and player col are not close to block row and block col,
        # do not run the rest of this! Likely uses a lot of resources.
        
        ax0, ay0, ax1, ay1 = (app.p.x-app.p.r, app.p.y-app.p.r, # player corners
                              app.p.x+app.p.r, app.p.y+app.p.r)
                              
        nx0, ny0, nx1, ny1 = (ax0 + app.p.xVel, ay0 + app.p.yVel, # player corners next tick
                              ax1 + app.p.xVel, ay1 + app.p.yVel)         

        bx0, by0, bx1, by1 = getCellBounds(app, block.row, block.col) # block corners
        blockX = (bx1 + bx0)/2 # block center X
        blockY = (by1 + by0)/2 # block center Y


        xDif = app.p.x - blockX
        yDif = app.p.y - blockY
        distance = distanceFormula(app.p.x, app.p.y, blockX, blockY)


        if distance <= app.p.r * 2:
            if abs(xDif) < app.p.r * 1.5 and xDif > 0:
                if app.p.xVel < 0:
                    theta = math.atan(yDif/xDif)
                    if -(math.pi/4) <= theta and theta <= math.pi/4 :
                        # print('Left Collision') 
                        if block.type == 'terrain':
                            app.p.collide('Left', bx1)
                        elif block.type == 'hazard':
                            playerDie(app)

            if abs(xDif) < app.p.r * 1.5 and xDif < 0: 
                theta = math.atan(yDif/xDif)
                if app.p.xVel > 0:
                    if -(math.pi/4) <= theta and theta <= math.pi/4 :
                        # print('Right Collision') 
                        
                        if block.type == 'terrain':
                            app.p.collide('Right', bx0)
                        elif block.type == 'hazard':
                            playerDie(app)

def checkTouchFloor(app):
    for block in app.terrain:
        
        ax0, ay0, ax1, ay1 = (app.p.x-app.p.r, app.p.y-app.p.r, # player corners
                              app.p.x+app.p.r, app.p.y+app.p.r)
                              
        nx0, ny0, nx1, ny1 = (ax0 + app.p.xVel, ay0 + app.p.yVel, # player corners next tick
                              ax1 + app.p.xVel, ay1 + app.p.yVel)         

        bx0, by0, bx1, by1 = getCellBounds(app, block.row, block.col) # block corners
        blockX = (bx1 + bx0)/2 # block center X
        blockY = (by1 + by0)/2 # block center Y

        xDif = app.p.x - blockX
        yDif = app.p.y - blockY
        distance = distanceFormula(app.p.x, app.p.y, blockX, blockY)


        if distance <= app.p.r * 2: # only check relatively close blocks
            if abs(yDif) <= app.p.r * 1.5 and yDif < 0:
                if app.p.yVel < 0:
                    theta = math.atan(xDif/yDif)
                    if -(math.pi/4) < theta and theta < math.pi/4 :
                        # print('Down Collision') 
                        if block.type == 'terrain':
                            app.p.collide('Down', by0)
                        elif block.type == 'hazard':
                            playerDie(app)
            
            if abs(yDif) <= app.p.r * 1.5 and yDif > 0:
                if app.p.yVel > 0:
                    theta = math.atan(xDif/yDif)
                    if -(math.pi/4) < theta and theta < math.pi/4 :
                        # print('Up Collision') 
                        if block.type == 'terrain':
                            app.p.collide('Up', by1)
                        elif block.type == 'hazard':
                            playerDie(app)
                        

def playerDie(app):
    if app.mode == 'gameMode':
        # extract player coordinates
        x, y = app.p.x, app.p.y
        # find row and column of death
        pRow, pCol = getCell(app, x, y)
        # based on where they died in terms of cols, respawn them in the space before the chunk they died in
        for i in range(len(app.endCols) - 1):
            curStartCol = app.endCols[i]
            nextStartCol = app.endCols[i+1]
            if curStartCol < pCol and pCol <= nextStartCol: # we found between which chunks they died in,
                # curStartCol is the beginning of the chunk they were on
                x0, y0, x1, y1 = getCellBounds(app, 59, curStartCol+5)
                app.p.die(x0, y0)
                return
        # can assume the player died in the last chunk:
        col = app.endCols[-1]
        x0, y0, x1, y1 = getCellBounds(app, 59, col + 3)
        app.p.die(x0, y0)



    elif app.mode == 'editorMode':
        app.p.die(400, app.p.groundLvl - 10)





def appStarted(app):
    app.p = Player(455, 560) # change these parameters to change the spawn position of player
    app.margin = 0
    app.mode = 'startScreenMode'
    app.difficulties = ['easy', 'normal', 'hard']
    app.diffIndex = 1
    app.chunkAssignedDifficulty = app.difficulties[app.diffIndex] # initialized 'normal'

    app.colHighScore = 0
    app.screensCrossed = 0

    app.gameDifficulties = ['easy', 'normal', 'hard']
    app.gameDiffIndex = 1
    app.gameDifficulty = app.gameDifficulties[app.gameDiffIndex]

    app.blockTypes = ['terrain', 'hazard'] # this changes through the types of terrain possible
    app.blockTypesIndex = 0 # so far: 'hazard' and 'terrain'
    app.blockAssignedType = app.blockTypes[app.blockTypesIndex]

    app.timerDelay = 17 # Runs at around 60 FPS... well ideally
    app.rows = (app.height-app.margin)//(app.p.r) # each cell is 1/4 the size
    app.cols = (app.width-app.margin)//(app.p.r) # of the player
    # or in other terms, the player is 2 blocks wide

    app.endCols = [0] # this will be a list of all of the starting positions of the chunks. Used to respawn a player at the beginning of a failed chunk

    app.terrain = []
    ### IMPORTANT FUNCTION ###
    app.chunkDict = {'easy': list(), 'normal': list(),
        'hard': list()} #
    # Keys will be either 'easy', 'normal', or 'hard'
    # the value corresponding to the key will be a list/set containing
    # all chunks of that difficulty. (or filler as a rest from challenge)

    app.chunkDict['easy'] = [

    [(60, 48, 'terrain'), (59, 49, 'terrain'), (59, 50, 'terrain'), (58, 51, 'terrain'), (57, 52, 'terrain'), (56, 53, 'terrain'), (55, 54, 'terrain'), (56, 55, 'terrain'), (57, 56, 'terrain'), (58, 57, 'terrain'), (59, 64, 'terrain'), (59, 67, 'terrain'), (60, 68, 'terrain'), (59, 60, 'hazard'), (59, 61, 'hazard'), (59, 62, 'hazard'), (59, 63, 'hazard'), (58, 65, 'terrain'), (58, 66, 'terrain'), (58, 58, 'terrain'), (59, 59, 'terrain')]
    ,
    [(60, 51, 'terrain'), (60, 52, 'terrain'), (59, 53, 'terrain'), (58, 54, 'terrain'), (58, 55, 'terrain'), (57, 60, 'terrain'), (56, 60, 'terrain'), (55, 61, 'terrain'), (54, 61, 'terrain'), (54, 62, 'terrain'), (53, 63, 'terrain'), (52, 63, 'terrain'), (51, 63, 'terrain'), (52, 64, 'terrain'), (53, 65, 'terrain'), (54, 66, 'terrain'), (55, 66, 'terrain'), (56, 67, 'terrain'), (57, 68, 'terrain'), (58, 68, 'terrain'), (58, 59, 'hazard'), (58, 58, 'hazard'), (58, 57, 'hazard'), (58, 56, 'hazard'), (59, 69, 'hazard'), (59, 71, 'hazard'), (59, 70, 'hazard'), (56, 62, 'hazard'), (58, 62, 'hazard'), (59, 63, 'hazard'), (59, 64, 'hazard'), (59, 65, 'hazard'), (58, 66, 'hazard'), (56, 66, 'hazard'), (60, 73, 'hazard'), (60, 74, 'terrain'), (60, 75, 'terrain'), (60, 72, 'hazard')]
    ,
    [(57, 51, 'terrain'), (58, 52, 'terrain'), (59, 53, 'terrain'), (59, 49, 'terrain'), (60, 48, 'terrain'), (60, 53, 'terrain'), (55, 58, 'terrain'), (55, 59, 'terrain'), (55, 60, 'terrain'), (55, 61, 'terrain'), (53, 68, 'terrain'), (53, 67, 'terrain'), (53, 70, 'terrain'), (53, 69, 'terrain'), (54, 78, 'terrain'), (54, 79, 'terrain'), (55, 80, 'terrain'), (56, 81, 'terrain'), (57, 82, 'terrain'), (58, 83, 'terrain'), (59, 84, 'terrain'), (60, 85, 'terrain'), (54, 62, 'terrain'), (52, 71, 'terrain'), (53, 77, 'terrain'), (53, 76, 'terrain'), (57, 50, 'terrain'), (58, 49, 'terrain')]
    ,
    [(60, 52, 'terrain'), (60, 53, 'terrain'), (59, 54, 'terrain'), (59, 56, 'terrain'), (59, 57, 'terrain'), (59, 55, 'terrain'), (59, 58, 'terrain'), (58, 59, 'terrain'), (57, 60, 'terrain'), (55, 61, 'terrain'), (53, 61, 'terrain'), (54, 61, 'terrain'), (54, 55, 'terrain'), (54, 54, 'terrain'), (52, 61, 'terrain'), (53, 53, 'terrain'), (52, 52, 'terrain'), (51, 51, 'terrain'), (49, 49, 'terrain'), (49, 50, 'terrain'), (50, 51, 'terrain'), (47, 47, 'terrain'), (46, 47, 'terrain'), (48, 48, 'terrain'), (42, 61, 'terrain'), (43, 60, 'terrain'), (43, 59, 'terrain'), (44, 58, 'terrain'), (44, 57, 'terrain'), (45, 55, 'terrain'), (45, 56, 'terrain'), (46, 54, 'terrain'), (56, 60, 'terrain'), (49, 60, 'terrain'), (50, 60, 'terrain'), (51, 60, 'terrain')]
    ,
    [(60, 47, 'terrain'), (59, 51, 'terrain'), (59, 48, 'terrain'), (58, 49, 'terrain'), (58, 50, 'terrain'), (59, 52, 'hazard'), (59, 53, 'hazard'), (59, 54, 'hazard'), (59, 55, 'hazard'), (59, 56, 'hazard'), (59, 57, 'terrain'), (58, 58, 'terrain'), (58, 59, 'terrain'), (58, 60, 'terrain'), (59, 61, 'terrain'), (60, 62, 'terrain')]
    ,
    [(60, 47, 'terrain'), (59, 47, 'terrain'), (59, 48, 'terrain'), (58, 48, 'terrain'), (57, 48, 'terrain'), (57, 49, 'terrain'), (56, 49, 'terrain'), (55, 49, 'terrain'), (55, 50, 'terrain'), (54, 50, 'terrain'), (53, 51, 'terrain'), (52, 51, 'terrain'), (51, 51, 'terrain'), 
    (46, 49, 'terrain'), (46, 50, 'terrain'), (46, 51, 'terrain'), (46, 52, 'terrain'), (46, 53, 'terrain'), (47, 54, 'terrain'), (47, 55, 'terrain'), (48, 56, 'terrain'), (48, 57, 'terrain'), (49, 58, 'terrain'), (50, 58, 'terrain'), (51, 59, 'terrain'), (52, 59, 'terrain'), (53, 59, 'terrain'), (54, 59, 'terrain'), (54, 58, 'terrain'), (55, 58, 'terrain'), (55, 57, 'terrain'), (56, 57, 'terrain'), (56, 56, 'terrain'), (57, 56, 'terrain'), (58, 56, 'terrain'), (58, 57, 'terrain'), (58, 58, 'terrain'), (58, 59, 'terrain'), (58, 60, 'terrain'), (57, 61, 'terrain'), (56, 62, 'terrain'), (56, 63, 'terrain'), (55, 63, 'terrain'), (55, 64, 'terrain'), (60, 68, 'hazard'), (60, 69, 'hazard'), (60, 70, 'hazard'), (60, 67, 'terrain'), (54, 65, 'terrain'), (54, 66, 'terrain'), (53, 66, 'terrain'), (53, 67, 'terrain'), (53, 68, 'terrain'), (60, 71, 'terrain')]
    ,
    [(60, 47, 'terrain'), (58, 47, 'terrain'), (58, 48, 'terrain'), (59, 47, 'terrain'), (58, 49, 'terrain'), (56, 53, 'terrain'), (55, 53, 'terrain'), (55, 55, 'terrain'), (55, 54, 'terrain'), (57, 53, 'terrain'), (53, 59, 'terrain'), (52, 59, 'terrain'), (52, 60, 'terrain'), (52, 61, 'terrain'), (54, 59, 'terrain'), (49, 65, 'terrain'), (50, 65, 'terrain'), (49, 66, 'terrain'), (49, 67, 'terrain'), (51, 65, 'terrain'), (56, 70, 'hazard'), (58, 68, 'hazard'), (60, 66, 'hazard'), (47, 71, 'terrain'), (48, 71, 'terrain'), (46, 71, 'terrain'), (46, 72, 'terrain'), (46, 73, 'terrain'), (54, 72, 'hazard'), (56, 74, 'hazard'), (58, 76, 'hazard'), (60, 78, 'hazard')]
    ,
    [(60, 53, 'terrain'), (60, 54, 'terrain'), (60, 55, 'terrain'), (57, 59, 'terrain'), (56, 59, 'terrain'), (55, 60, 'terrain'), (54, 60, 'terrain'), (53, 60, 'terrain'), (48, 55, 'terrain'), (48, 54, 'terrain'), (48, 53, 'terrain'), (49, 52, 'terrain'), (49, 51, 'terrain'), (50, 50, 'terrain'), (54, 48, 'terrain'), (55, 48, 'terrain'), (54, 54, 'terrain'), (54, 53, 'terrain'), (54, 52, 'terrain'), (47, 59, 'terrain'), (48, 60, 'terrain'), (48, 61, 'terrain'), (45, 68, 'terrain'), (46, 68, 'terrain'), (47, 67, 'terrain'), (48, 65, 'terrain'), (48, 66, 'terrain'), (59, 56, 'terrain'), (59, 57, 'terrain'), (58, 58, 'terrain'), (50, 49, 'terrain'), (52, 45, 'terrain'), (51, 45, 'terrain'), (53, 46, 'terrain'), (50, 45, 'terrain'), (49, 45, 'terrain'), (51, 66, 'hazard'), (53, 68, 'hazard'), (55, 70, 'hazard'), (57, 72, 'hazard'), (49, 64, 'hazard'), (49, 63, 'hazard'), (49, 62, 'hazard'), (59, 74, 'hazard'), (54, 51, 'terrain'), (54, 50, 'terrain'), (56, 49, 'hazard'), (57, 49, 'hazard'), (58, 50, 'hazard')]
    ,
    [(60, 50, 'terrain'), (59, 49, 'terrain'), (58, 48, 'terrain'), (57, 49, 'terrain'), (56, 50, 'terrain'), (57, 51, 'terrain'), (58, 52, 'terrain'), (59, 51, 'terrain'), (58, 50, 'hazard'), (58, 56, 'terrain'), (57, 57, 'terrain'), (56, 58, 'terrain'), (57, 59, 'terrain'), (58, 60, 'terrain'), (60, 58, 'terrain'), (59, 59, 'terrain'), (59, 57, 'terrain'), (58, 58, 'hazard'), (58, 64, 'terrain'), (57, 65, 'terrain'), (56, 66, 'terrain'), (57, 67, 'terrain'), (58, 68, 'terrain'), (59, 67, 'terrain'), (60, 66, 'terrain'), (59, 65, 'terrain'), (58, 66, 'hazard'), (58, 72, 'terrain'), (57, 73, 'terrain'), (56, 74, 'terrain'), (57, 75, 'terrain'), (58, 76, 'terrain'), (59, 75, 'terrain'), (60, 74, 'terrain'), (59, 73, 'terrain'), (58, 74, 'hazard')]
    ,
    [(60, 48, 'terrain'), (59, 49, 'terrain'), (59, 50, 'terrain'), (58, 51, 'terrain'), (57, 52, 'terrain'), (56, 52, 'terrain'), (56, 53, 'terrain'), (55, 54, 'terrain'), (56, 55, 'terrain'), (57, 56, 'terrain'), (60, 68, 'terrain'), (59, 60, 'hazard'), (59, 61, 'hazard'), (59, 62, 'hazard'), (59, 63, 'hazard'), (58, 64, 'terrain'), (58, 65, 'terrain'), (58, 66, 'terrain'), (58, 58, 'terrain'), (58, 59, 'terrain'), (59, 67, 'terrain'), (58, 57, 'terrain')]
    ,
    [(58, 47, 'terrain'), (58, 48, 'terrain'), (58, 49, 'terrain'), (58, 50, 'terrain'), (58, 51, 'terrain'), (58, 56, 'terrain'), (57, 56, 'terrain'), (56, 56, 'terrain'), (54, 54, 'terrain'), (54, 53, 'terrain'), (54, 52, 'terrain'), (54, 51, 'terrain'), (54, 50, 'terrain'), (56, 45, 'terrain'), (57, 46, 'terrain'), (55, 45, 'terrain'), (54, 45, 'terrain'), (53, 45, 'terrain'), (52, 45, 
    'terrain'), (59, 56, 'terrain'), (55, 55, 'terrain'), (53, 63, 'terrain'), (56, 68, 'terrain'), (54, 68, 'terrain'), (53, 68, 'terrain'), (52, 68, 'terrain'), (55, 68, 'terrain'), (52, 63, 'terrain'), (58, 67, 'terrain'), (54, 64, 'terrain'), (50, 68, 'terrain'), 
    (49, 63, 'terrain'), (50, 63, 'terrain'), (51, 63, 'terrain'), (49, 68, 'terrain'), (48, 68, 'terrain'), (47, 68, 'terrain'), (51, 67, 'terrain'), (47, 63, 'terrain'), (48, 64, 'terrain'), (46, 63, 'terrain'), (45, 63, 'terrain'), (46, 68, 'terrain'), (44, 63, 'terrain'), (43, 63, 'terrain'), (42, 63, 'terrain'), (45, 69, 'terrain'), (57, 67, 'terrain'), (59, 66, 'terrain'), (60, 65, 'terrain'), (41, 64, 'terrain')]
    ,
    [(60, 57, 'terrain'), (59, 59, 'terrain'), (60, 56, 'hazard'), (60, 55, 'hazard'), (60, 54, 'hazard'), (60, 53, 'hazard'), (60, 52, 'hazard'), (60, 63, 'hazard'), (60, 64, 'hazard'), (60, 65, 'hazard'), (60, 66, 'hazard'), (60, 67, 'hazard'), (60, 68, 'terrain'), (59, 70, 'terrain'), (59, 69, 'terrain'), (58, 71, 'terrain'), (58, 72, 'terrain'), (59, 73, 'terrain'), (60, 74, 'terrain'), (59, 51, 'terrain'), (60, 51, 'terrain'), (60, 47, 'terrain'), (59, 47, 'terrain'), (58, 48, 'terrain'), (58, 50, 'terrain'), (58, 49, 'terrain'), (60, 46, 'hazard'), (60, 45, 'hazard'), (59, 62, 'terrain'), (60, 62, 'terrain'), (60, 58, 'terrain'), (58, 60, 'terrain'), (58, 61, 'terrain')]
    ,
    [(60, 50, 'terrain'), (59, 50, 'terrain'), (57, 52, 'terrain'), (57, 49, 'terrain'), (60, 57, 'hazard'), (59, 57, 'hazard'), (59, 58, 'hazard'), (60, 58, 'hazard'), (60, 66, 'hazard'), (59, 66, 'hazard'), (56, 73, 'terrain'), (56, 72, 'terrain'), (56, 74, 'terrain'), (56, 75, 'terrain'), (58, 74, 'terrain'), (59, 74, 'terrain'), (60, 74, 'terrain'), (58, 72, 'terrain'), (59, 72, 'terrain'), (60, 72, 'terrain'), (56, 71, 'terrain'), (59, 46, 'terrain'), (60, 46, 'terrain'), (60, 45, 'terrain'), (59, 45, 'terrain'), (59, 65, 'hazard'), 
    (60, 65, 'hazard'), (57, 71, 'terrain'), (57, 75, 'terrain'), (58, 49, 'terrain'), (57, 50, 'terrain'), (57, 51, 'terrain'), (59, 52, 'terrain'), (60, 52, 'terrain'), (58, 53, 'terrain'), (57, 53, 'terrain'), (60, 69, 'terrain'), (60, 70, 'terrain'), (59, 70, 'terrain'), (59, 69, 'terrain'), (60, 78, 'hazard'), (59, 78, 'hazard'), (60, 79, 'hazard'), (59, 79, 'hazard')]
    ,
    [(60, 51, 'terrain'), (59, 52, 'terrain'), (57, 57, 'terrain'), (57, 58, 'terrain'), (57, 59, 'terrain'), (56, 59, 'terrain'), (55, 66, 'terrain'), (54, 66, 'terrain'), (56, 65, 'terrain'), (56, 66, 'terrain'), (56, 64, 'terrain'), (58, 73, 'terrain'), (58, 72, 'terrain'), (60, 53, 'hazard'), (60, 59, 'hazard'), (60, 61, 'hazard'), (60, 63, 'hazard'), (60, 65, 'hazard'), (60, 69, 'hazard'), (60, 71, 'hazard'), (60, 57, 'hazard'), (60, 55, 'hazard'), (60, 67, 'hazard'), (58, 74, 'terrain'), (59, 74, 'terrain'), (60, 74, 'terrain'), (60, 73, 'hazard')]
    ,
    [(60, 53, 'hazard'), (60, 56, 'hazard'), (60, 65, 'hazard'), (60, 62, 'hazard'), (59, 64, 'hazard'), (59, 63, 'hazard'), (59, 55, 'hazard'), (59, 54, 'hazard'), (59, 45, 'terrain'), (60, 45, 'terrain'), (59, 46, 'terrain'), (60, 46, 'terrain'), (59, 72, 'terrain'), 
    (60, 72, 'terrain'), (60, 73, 'terrain'), (59, 73, 'terrain')]
    ,
    [(59, 50, 'hazard'), (59, 51, 'hazard'), (59, 52, 'hazard'), (60, 54, 'terrain'), (60, 55, 'terrain'), (60, 56, 'terrain'), (59, 57, 'terrain'), (58, 57, 'terrain'), (57, 59, 'terrain'), (57, 58, 'terrain'), (57, 60, 'terrain'), (58, 61, 'terrain'), (59, 61, 'terrain'), (56, 63, 'hazard'), (56, 62, 'hazard'), (56, 64, 'hazard'), (50, 62, 'hazard'), (50, 63, 'hazard'), (50, 64, 'hazard'), (53, 51, 'hazard'), (53, 52, 'hazard'), (53, 50, 'hazard'), (60, 61, 'terrain')]
    ,
    [(51, 46, 'terrain'), (50, 48, 'terrain'), (51, 48, 'terrain'), (52, 48, 'terrain'), (53, 48, 'terrain'), (54, 48, 'terrain'), (55, 48, 'terrain'), (56, 48, 'terrain'), (60, 48, 'terrain'), (60, 47, 'terrain'), (60, 46, 'terrain'), (60, 50, 'terrain'), (60, 49, 'terrain'), 
    (50, 47, 'terrain'), (52, 45, 'terrain'), (57, 48, 'terrain'), (54, 57, 'terrain'), (55, 57, 'terrain'), (58, 54, 'terrain'), (58, 53, 'terrain'), (58, 52, 'terrain'), (57, 56, 'terrain'), (58, 55, 'terrain'), (56, 57, 'terrain'), (54, 54, 'terrain'), (54, 53, 'terrain'), (53, 52, 'terrain'), (54, 52, 'terrain'), (52, 52, 'terrain'), (51, 52, 'terrain'), (50, 55, 'terrain'), (50, 56, 'terrain'), (49, 57, 'terrain'), (50, 51, 'terrain'), (47, 70, 'terrain'), (48, 69, 'terrain'), (49, 69, 'terrain'), (50, 69, 'terrain'), (51, 68, 'terrain'), (41, 70, 'terrain'), (42, 69, 'terrain'), (51, 67, 'terrain'), (51, 69, 'terrain'), (46, 75, 'terrain'), (45, 75, 'terrain'), (44, 76, 'terrain'), (44, 77, 'terrain'), (45, 78, 'terrain'), (45, 79, 'terrain'), (46, 79, 'terrain'), (47, 79, 'terrain'), (48, 79, 'terrain'), (49, 79, 'terrain'), (51, 79, 'terrain'), (52, 78, 'terrain'), (50, 79, 'terrain'), (53, 77, 'terrain'), (54, 76, 'terrain'), (55, 76, 'terrain'), (55, 75, 'terrain'), (56, 75, 'terrain'), (57, 74, 'terrain'), (57, 73, 'terrain'), (58, 72, 'terrain'), (58, 71, 'terrain'), (57, 71, 'terrain'), (56, 71, 'terrain'), (55, 72, 'terrain'), (54, 73, 'terrain'), (54, 74, 'terrain'), (56, 76, 'terrain'), (57, 77, 'terrain'), (57, 78, 'terrain'), (58, 78, 'terrain'), (58, 79, 'terrain'), (58, 80, 'terrain'), (58, 81, 'terrain'), (52, 62, 'terrain'), (51, 
    62, 'terrain'), (50, 62, 'terrain'), (49, 62, 'terrain'), (48, 62, 'terrain'), (45, 62, 'terrain'), (46, 62, 'terrain'), (46, 61, 'terrain'), (53, 61, 'terrain'), (51, 63, 'terrain'), (51, 64, 'terrain'), (47, 60, 'terrain'), (47, 62, 'terrain'), (43, 68, 'terrain'), (45, 70, 'terrain'), (44, 70, 'terrain'), (43, 70, 'terrain'), (46, 70, 'terrain'), (42, 70, 'terrain'), (43, 67, 'terrain'), (51, 70, 'terrain'), (51, 71, 'terrain'), (51, 47, 'terrain'), (52, 46, 'terrain')]
    ,
    [(60, 48, 'terrain'), (59, 51, 'terrain'), (60, 52, 'terrain'), (60, 51, 'terrain'), (59, 52, 'terrain'), (60, 54, 'terrain'), (60, 55, 'terrain'), (59, 48, 'terrain'), (59, 54, 'terrain'), (59, 55, 'terrain'), (60, 58, 'terrain'), (59, 58, 'terrain'), (58, 58, 'terrain'), (57, 58, 'terrain'), (56, 59, 'terrain'), (55, 60, 'terrain'), (54, 61, 'terrain'), (54, 62, 'terrain'), (54, 63, 
    'terrain'), (54, 64, 'terrain'), (54, 65, 'terrain'), (54, 66, 'terrain'), (59, 71, 'terrain'), (60, 71, 'terrain'), (58, 71, 'terrain'), (57, 71, 'terrain'), (56, 70, 'terrain'), (55, 69, 'terrain'), (54, 68, 'terrain'), (54, 67, 'terrain'), (60, 74, 'terrain'), 
    (59, 75, 'terrain'), (60, 75, 'terrain'), (60, 77, 'terrain'), (59, 77, 'terrain'), (59, 78, 'terrain'), (60, 78, 'terrain'), (59, 81, 'terrain'), (60, 81, 'terrain'), (60, 62, 'hazard'), (60, 63, 'hazard'), (60, 64, 'hazard'), (60, 65, 'hazard'), (60, 66, 'hazard'), (60, 67, 'hazard'), (59, 68, 'hazard'), (59, 61, 'hazard'), (59, 74, 'terrain'), (59, 80, 'terrain'), (60, 80, 'terrain'), (60, 
    49, 'terrain'), (59, 49, 'terrain'), (58, 65, 'hazard'), (58, 64, 'hazard'), (57, 63, 'hazard'), (57, 62, 'hazard'), (57, 66, 'hazard'), (57, 67, 'hazard')]
    ,
    [(59, 53, 'terrain'), (58, 54, 'terrain'), (57, 55, 'terrain'), (56, 56, 'terrain'), (55, 56, 'terrain'), (54, 56, 'terrain'), (52, 57, 'terrain'), (51, 58, 'terrain'), (50, 58, 'terrain'), (50, 59, 'terrain'), (49, 59, 'terrain'), (48, 59, 'terrain'), (47, 60, 'terrain'), (46, 61, 'terrain'), (45, 61, 'terrain'), (44, 62, 'terrain'), (43, 62, 'terrain'), (42, 63, 'terrain'), (60, 52, 'terrain'), (53, 57, 'terrain'), (46, 65, 'hazard'), (47, 65, 'hazard'), (45, 66, 'hazard'), (45, 67, 'hazard'), (46, 68, 'hazard'), (45, 70, 'hazard'), (45, 69, 'hazard'), (46, 71, 'hazard'), (47, 71, 'hazard'), (48, 66, 'hazard'), (49, 67, 'hazard'), (50, 68, 'hazard'), (49, 69, 'hazard'), (48, 70, 'hazard'), (42, 64, 'terrain'), (42, 65, 'terrain')]
    ,
    [(58, 48, 'terrain'), (58, 50, 'terrain'), (56, 56, 'terrain'), (56, 55, 'terrain'), (56, 57, 'terrain'), (57, 49, 'terrain'), (58, 49, 'terrain'), (55, 56, 'terrain'), (55, 61, 'terrain'), (55, 62, 'terrain'), (55, 63, 'terrain'), (56, 68, 'terrain'), (56, 67, 'terrain'), (56, 69, 'terrain'), (57, 68, 'terrain'), (58, 75, 'terrain'), (58, 74, 'terrain'), (58, 76, 'terrain'), (59, 75, 'terrain'), (54, 62, 'terrain'), (56, 62, 'terrain'), (60, 49, 'hazard'), (60, 51, 'hazard'), (60, 53, 'hazard'), (60, 55, 'hazard'), (60, 57, 'hazard'), (60, 59, 'hazard'), (60, 63, 'hazard'), (60, 65, 'hazard'), (60, 69, 'hazard'), (60, 73, 'hazard'), (60, 75, 'hazard'), (60, 71, 'hazard'), (60, 67, 'hazard'), (60, 61, 'hazard')]


    ]

    app.chunkDict['normal'] = [

    [(59, 47, 'terrain'), (58, 47, 'terrain'), (57, 47, 'terrain'), (60, 47, 'terrain'), (60, 59, 'terrain'), (55, 59, 'terrain'), (56, 59, 'terrain'), (57, 59, 'terrain'), (58, 59, 'terrain'), (59, 59, 'terrain'), (54, 59, 'terrain'), (60, 71, 'terrain'), (59, 71, 'terrain'), (58, 71, 'terrain'), (57, 71, 'terrain'), (56, 71, 'terrain'), (55, 71, 'terrain'), (54, 71, 'terrain'), (53, 71, 'terrain'), (52, 71, 'terrain'), (51, 71, 'terrain'), (57, 46, 'terrain'), (54, 58, 'terrain'), (51, 70, 'terrain')]
    ,
    [(56, 57, 'terrain'), (55, 57, 'terrain'), (54, 57, 'terrain'), (53, 57, 'terrain'), (52, 56, 'terrain'), (55, 51, 'terrain'), (54, 51, 'terrain'), (53, 51, 'terrain'), (52, 51, 'terrain'), (51, 51, 'terrain'), (50, 51, 'terrain'), (49, 51, 'terrain'), (48, 51, 'terrain'), (47, 52, 'terrain'), (51, 57, 'terrain'), (50, 57, 'terrain'), (49, 57, 'terrain'), (48, 57, 'terrain'), (47, 57, 'terrain'), (46, 57, 'terrain'), (45, 57, 'terrain'), (44, 57, 'terrain'), (43, 57, 'terrain'), (41, 57, 'terrain'), (40, 57, 'terrain'), (46, 51, 'terrain'), (45, 51, 'terrain'), (44, 51, 'terrain'), (43, 51, 'terrain'), (42, 51, 'terrain'), (42, 56, 'terrain'), (56, 50, 'terrain'), (56, 49, 'terrain'), (55, 48, 'terrain'), (57, 57, 'terrain'), (58, 57, 'terrain'), (59, 56, 'terrain'), (60, 55, 'terrain'), (41, 51, 'terrain'), (40, 51, 'terrain'), (40, 58, 'terrain'), (40, 59, 'terrain')]
    ,
    [(59, 47, 'terrain'), (58, 47, 'terrain'), (57, 48, 'terrain'), (57, 49, 'terrain'), (57, 50, 'terrain'), (60, 51, 'terrain'), (59, 51, 'terrain'), (58, 51, 'terrain'), (60, 47, 'terrain'), (60, 52, 'hazard'), (60, 53, 'hazard'), (60, 54, 'hazard'), (60, 55, 'hazard'), (60, 56, 'hazard'), (60, 57, 'hazard'), (60, 58, 'hazard'), (60, 59, 'hazard'), (60, 61, 'hazard'), (60, 60, 'hazard'), (60, 63, 'hazard'), (60, 64, 'hazard'), (60, 65, 'hazard'), (60, 66, 'hazard'), (60, 67, 'hazard'), (60, 62, 'hazard'), (60, 68, 'hazard'), (60, 69, 'hazard'), (60, 71, 'hazard'), (60, 72, 'hazard'), (60, 70, 'hazard'), (60, 73, 'hazard'), (60, 74, 'hazard'), (60, 76, 'hazard'), (60, 75, 'hazard'), (60, 77, 'hazard'), (60, 78, 'hazard'), (60, 79, 'terrain'), (58, 79, 'terrain'), (59, 79, 'terrain'), (57, 80, 'terrain'), (57, 81, 'terrain'), (57, 82, 'terrain'), (58, 83, 'terrain'), (59, 83, 'terrain'), (60, 83, 'terrain'), (53, 64, 'terrain'), (54, 72, 'terrain'), (55, 58, 'terrain'), (55, 57, 'terrain'), (54, 71, 'terrain')]
    ,
    [(60, 50, 'hazard'), (60, 55, 'hazard'), (59, 54, 'hazard'), (59, 53, 'hazard'), (59, 52, 'hazard'), (59, 51, 'hazard'), (54, 51, 'hazard'), (54, 52, 'hazard'), (54, 53, 'hazard'), (54, 54, 'hazard'), (53, 55, 'hazard'), (53, 50, 'hazard'), (59, 74, 'hazard'), (59, 
    73, 'hazard'), (59, 72, 'hazard'), (59, 71, 'hazard'), (54, 71, 'hazard'), (54, 72, 'hazard'), (54, 73, 'hazard'), (54, 74, 'hazard'), (53, 75, 'hazard'), (53, 70, 'hazard'), (60, 75, 'hazard'), (60, 70, 'hazard')]
    ,
    [(56, 58, 'terrain'), (55, 58, 'terrain'), (57, 58, 'terrain'), (52, 53, 'terrain'), (53, 53, 'terrain'), (54, 53, 'terrain'), (54, 58, 'hazard'), (51, 53, 'hazard'), (51, 58, 'terrain'), (50, 58, 'terrain'), (49, 58, 'terrain'), (48, 58, 'hazard'), (52, 58, 'hazard'), (53, 58, 'hazard'), (50, 53, 'hazard'), (49, 53, 'hazard'), (47, 53, 'terrain'), (46, 53, 'terrain'), (48, 53, 'terrain'), (47, 58, 'hazard'), (46, 58, 'hazard'), (45, 58, 'terrain'), (44, 58, 'terrain'), (43, 58, 'terrain'), (45, 53, 'hazard'), (44, 53, 'hazard'), (43, 53, 'hazard'), (60, 56, 'terrain'), (60, 55, 'terrain'), (60, 57, 'terrain'), (59, 58, 'terrain'), (58, 58, 'terrain'), (41, 53, 'terrain'), (42, 53, 'terrain'), (40, 53, 'terrain'), (42, 58, 'hazard'), (39, 59, 'terrain'), (39, 60, 'terrain'), (39, 61, 'terrain'), (39, 62, 'terrain'), (39, 63, 'terrain'), (39, 58, 'terrain'), (40, 58, 'hazard'), (41, 58, 'hazard'), (60, 58, 'terrain')]
    ,
    [(57, 49, 'terrain'), (56, 49, 'terrain'), (55, 49, 'terrain'), (58, 48, 'terrain'), (54, 50, 'terrain'), (53, 50, 'terrain'), (52, 50, 'terrain'), (51, 51, 'terrain'), (50, 51, 'terrain'), (49, 51, 'terrain'), (49, 52, 'terrain'), (43, 58, 'hazard'), (44, 58, 'hazard'), (45, 58, 'hazard'), (46, 58, 'hazard'), (49, 63, 'terrain'), (49, 64, 'terrain'), (49, 65, 'terrain'), (44, 72, 'hazard'), (45, 72, 'hazard'), (43, 72, 'hazard'), (46, 72, 'hazard'), (50, 77, 'terrain'), (50, 79, 'terrain'), (50, 78, 'terrain'), (50, 80, 'terrain'), (49, 66, 'terrain'), (60, 82, 'hazard'), (59, 82, 'hazard'), (58, 82, 'hazard'), (57, 81, 'hazard'), (56, 81, 'hazard'), (55, 80, 'hazard'), (54, 80, 'hazard'), (53, 79, 'hazard'), (52, 79, 'hazard')]
    ,
    [(57, 68, 'terrain'), (56, 69, 'terrain'), (55, 69, 'terrain'), (54, 70, 'terrain'), (53, 70, 'terrain'), (51, 71, 'terrain'), (50, 71, 'terrain'), (49, 71, 'terrain'), (48, 71, 'terrain'), (47, 71, 'terrain'), (45, 70, 'terrain'), (44, 70, 'terrain'), (43, 69, 'terrain'), (42, 69, 'terrain'), (42, 51, 'terrain'), (43, 51, 'terrain'), (45, 50, 'terrain'), (44, 50, 'terrain'), (47, 49, 'terrain'), (48, 49, 'terrain'), (49, 49, 'terrain'), (50, 49, 'terrain'), (51, 49, 'terrain'), (53, 50, 'terrain'), (54, 50, 'terrain'), (55, 51, 'terrain'), (56, 51, 'terrain'), (57, 52, 'terrain'), (58, 53, 'terrain'), (58, 54, 'terrain'), (46, 71, 'terrain'), (52, 71, 'terrain'), (52, 49, 'terrain'), (46, 49, 'terrain'), (59, 60, 'hazard'), (57, 60, 'hazard'), (55, 60, 'hazard'), (53, 60, 'hazard'), (51, 60, 'hazard'), (49, 60, 'hazard'), (58, 67, 'terrain'), (58, 66, 'terrain'), (41, 51, 'hazard'), (41, 69, 'hazard'), (60, 59, 'terrain'), (60, 60, 'terrain'), (60, 61, 'terrain')]
    ,
    [(43, 59, 'terrain'), (44, 59, 'terrain'), (45, 59, 'terrain'), (46, 59, 'terrain'), (38, 53, 'hazard'), (39, 53, 'hazard'), (50, 69, 'terrain'), (52, 77, 'terrain'), (51, 80, 'terrain'), (51, 79, 'terrain'), (51, 78, 'terrain'), (53, 77, 'terrain'), (54, 76, 'terrain'), (40, 53, 'hazard'), (41, 53, 'hazard'), (58, 43, 'terrain'), (57, 43, 'terrain'), (56, 43, 'terrain'), (54, 44, 'terrain'), (53, 44, 'terrain'), (52, 44, 'terrain'), (50, 45, 'terrain'), (49, 45, 'terrain'), (48, 45, 'terrain'), (45, 46, 'terrain'), (44, 46, 'terrain'), (46, 46, 'terrain'), (44, 47, 'terrain'), (49, 69, 'terrain'), (48, 69, 'terrain'), (47, 69, 'terrain'), (45, 69, 'hazard'), (43, 69, 'hazard'), (41, 69, 'hazard'), (41, 59, 'hazard'), (39, 59, 'hazard'), (37, 59, 'hazard'), (56, 76, 'hazard'), (58, 76, 'hazard'), (60, 76, 'hazard')]
    ,
    [(58, 47, 'terrain'), (57, 48, 'terrain'), (58, 49, 'terrain'), (59, 48, 'terrain'), (55, 56, 'terrain'), (54, 55, 'terrain'), (55, 54, 'terrain'), (56, 55, 'terrain'), (54, 65, 'terrain'), (55, 66, 'terrain'), (55, 64, 'terrain'), (56, 65, 'terrain'), (52, 75, 'terrain'), (53, 76, 'terrain'), (51, 76, 'terrain'), (52, 77, 'terrain'), (54, 76, 'hazard'), (56, 76, 'hazard'), (58, 76, 'hazard'), (60, 76, 'hazard'), (57, 65, 'hazard'), (59, 65, 'hazard'), (57, 55, 'hazard'), (59, 55, 'hazard'), (60, 48, 'hazard')]
    ,
    [(56, 46, 'terrain'), (57, 46, 'terrain'), (56, 47, 'terrain'), (55, 53, 'terrain'), (55, 54, 'terrain'), (55, 55, 'terrain'), (56, 54, 'terrain'), (51, 58, 'hazard'), (51, 61, 'hazard'), (55, 64, 'terrain'), (55, 65, 'terrain'), (55, 66, 'terrain'), (56, 65, 'terrain'), (52, 59, 'hazard'), (52, 60, 'hazard'), (53, 70, 'hazard'), (47, 69, 'hazard'), (48, 70, 'hazard'), (46, 69, 'hazard'), (60, 43, 'terrain'), (60, 44, 'terrain'), (60, 45, 'terrain'), (55, 73, 'terrain'), (55, 74, 'terrain'), (55, 75, 'terrain'), (56, 74, 'terrain'), (60, 82, 'terrain'), (60, 74, 'hazard'), (58, 74, 'hazard'), (54, 69, 'hazard'), (55, 69, 'hazard'), (60, 81, 'terrain'), (60, 83, 'terrain')]
    ,
    [(58, 61, 'terrain'), (57, 62, 'terrain'), (52, 67, 'terrain'), (51, 68, 'terrain'), (48, 58, 'terrain'), (48, 60, 'terrain'), (49, 61, 'terrain'), (48, 59, 'terrain'), (44, 62, 'terrain'), (43, 62, 'terrain'), (42, 62, 'terrain'), (41, 62, 'terrain'), (40, 62, 'terrain'), (39, 62, 'terrain'), (38, 62, 'terrain'), (37, 62, 'terrain'), (37, 63, 'terrain'), (54, 65, 'terrain'), (56, 63, 'hazard'), (55, 64, 'terrain'), (53, 66, 'hazard'), (37, 64, 'terrain'), (50, 69, 'hazard'), (46, 69, 'hazard'), (48, 69, 'hazard'), (59, 61, 'terrain')]
    ,
    [(50, 54, 'terrain'), (50, 53, 'terrain'), (50, 52, 'terrain'), (50, 51, 'terrain'), (50, 50, 'terrain'), (50, 49, 'terrain'), (46, 49, 'terrain'), (46, 50, 'terrain'), (46, 51, 'terrain'), (46, 52, 'terrain'), (45, 56, 'hazard'), (45, 57, 'hazard'), (45, 58, 'hazard'), (46, 61, 'terrain'), (46, 62, 'terrain'), (46, 63, 'terrain'), (46, 64, 'terrain'), (46, 53, 'terrain'), (51, 70, 'hazard'), (53, 70, 'hazard'), (55, 70, 'hazard'), (56, 74, 'hazard'), (57, 70, 'hazard'), (52, 61, 'terrain'), (53, 61, 'terrain'), (54, 61, 'terrain'), (55, 61, 'terrain'), (56, 61, 'terrain'), (57, 61, 'terrain'), (48, 75, 'hazard'), (47, 77, 'hazard'), (50, 74, 'hazard'), (52, 74, 'hazard'), (54, 74, 'hazard'), (58, 74, 'hazard'), (59, 70, 'hazard'), (48, 67, 'hazard'), (47, 65, 'hazard'), (49, 69, 'hazard')]
    ,
    [(50, 52, 'terrain'), (48, 55, 'terrain'), (48, 56, 'terrain'), (47, 57, 'terrain'), (46, 58, 'terrain'), (49, 54, 'hazard'), (46, 62, 'hazard'), (49, 61, 'hazard'), (45, 63, 'hazard'), (44, 64, 'hazard'), (43, 63, 'hazard'), (42, 64, 'hazard'), (41, 65, 'hazard'), 
    (55, 58, 'terrain'), (57, 57, 'terrain'), (58, 56, 'terrain'), (56, 58, 'terrain'), (53, 58, 'terrain'), (52, 59, 'terrain'), (47, 62, 'terrain'), (50, 61, 'terrain'), (48, 62, 'terrain'), (44, 62, 'terrain'), (44, 61, 'terrain'), (44, 60, 'terrain'), (45, 59, 'hazard'), (52, 57, 'hazard'), (47, 61, 'hazard'), (47, 59, 'hazard'), (49, 58, 'hazard'), (50, 54, 'terrain'), (51, 57, 'terrain'), (50, 57, 'terrain'), (50, 56, 'hazard'), (56, 48, 'terrain'), (54, 48, 'terrain'), (55, 48, 'terrain'), (50, 51, 'terrain'), (51, 50, 'terrain'), (52, 49, 'terrain'), (53, 48, 'terrain'), (59, 55, 'terrain'), (58, 49, 'terrain'), (59, 50, 'terrain'), (57, 48, 'terrain'), (60, 53, 'terrain'), (60, 52, 'terrain'), (60, 51, 'terrain'), (54, 58, 'terrain'), (60, 54, 'terrain'), (51, 60, 'hazard'), (51, 59, 'hazard')]
    ,
    [(60, 45, 'terrain'), (60, 51, 'hazard'), (59, 51, 'hazard'), (60, 59, 'hazard'), (59, 59, 'hazard'), (58, 59, 'hazard'), (60, 67, 'hazard'), (59, 67, 'hazard'), (58, 67, 'hazard'), (59, 74, 'hazard'), (60, 74, 'hazard'), (60, 80, 'terrain')]
    ,
    [(60, 51, 'terrain'), (59, 52, 'terrain'), (58, 53, 'terrain'), (56, 56, 'terrain'), (55, 57, 'terrain'), (54, 58, 'terrain'), (53, 59, 'terrain'), (52, 61, 'terrain'), (48, 65, 'terrain'), (47, 66, 'terrain'), (45, 67, 'terrain'), (44, 68, 'terrain'), (43, 68, 'terrain'), (56, 55, 'terrain'), (59, 50, 'terrain'), (57, 49, 'terrain'), (56, 48, 'terrain'), (56, 47, 'terrain'), (55, 48, 'terrain'), (52, 62, 'terrain'), (53, 62, 'terrain'), (54, 62, 'terrain'), (56, 63, 'terrain'), (57, 63, 'terrain'), (57, 64, 'terrain'), (56, 65, 'terrain'), (55, 65, 'terrain'), (54, 65, 'terrain'), (53, 65, 'terrain'), (52, 65, 'terrain'), (51, 65, 'terrain'), (50, 65, 'terrain'), (49, 64, 'terrain'), (42, 68, 'terrain'), (42, 67, 'terrain'), (42, 66, 'terrain'), (43, 65, 'terrain'), (45, 63, 'terrain'), (47, 61, 'terrain'), (48, 60, 'terrain'), (49, 59, 'terrain'), (50, 58, 'terrain'), (50, 57, 'terrain'), (52, 56, 'terrain'), (52, 55, 'terrain'), (53, 55, 'terrain'), (54, 54, 'terrain'), (54, 53, 'terrain'), (46, 62, 'terrain'), (46, 61, 'terrain'), (46, 60, 'terrain'), (46, 59, 'terrain'), (46, 58, 'terrain'), (46, 57, 'terrain'), (46, 56, 'terrain'), (46, 55, 'terrain'), (46, 54, 'terrain'), (47, 53, 'terrain'), (43, 66, 'hazard'), (46, 66, 'terrain'), (44, 64, 'terrain'), (55, 63, 'terrain'), (52, 60, 'terrain'), (48, 54, 'terrain'), (48, 55, 'terrain'), (48, 56, 'terrain'), (48, 52, 'terrain'), (48, 57, 'terrain'), (57, 54, 'terrain'), (55, 49, 'hazard'), (48, 53, 'terrain'), (51, 59, 'hazard'), (53, 57, 'hazard'), (49, 61, 'hazard'), (60, 47, 'hazard'), (58, 47, 'hazard'), (60, 49, 'hazard'), (55, 51, 'hazard'), (51, 57, 'terrain'), (58, 50, 'terrain'), (51, 62, 'terrain')]
    ,
    [(60, 49, 'terrain'), (59, 49, 'terrain'), (58, 49, 'terrain'), (57, 49, 'terrain'), (56, 49, 'terrain'), (55, 49, 'terrain'), (54, 49, 'terrain'), (53, 49, 'hazard'), (60, 62, 'terrain'), (59, 62, 'terrain'), (58, 62, 'terrain'), (57, 62, 'terrain'), (56, 62, 'terrain'), (55, 62, 'terrain'), (54, 62, 'terrain'), (53, 62, 'hazard'), (60, 43, 'terrain'), (60, 44, 'terrain'), (60, 68, 'terrain'), (60, 69, 'terrain'), (60, 67, 'terrain')]
    ,
    [(55, 65, 'terrain'), (56, 65, 'terrain'), (57, 65, 'terrain'), (58, 66, 'terrain'), (59, 66, 'terrain'), (54, 65, 'terrain'), (53, 65, 'terrain'), (56, 58, 'terrain'), (55, 58, 'terrain'), (54, 58, 'terrain'), (53, 58, 'terrain'), (52, 58, 'terrain'), (51, 64, 'terrain'), 
    (50, 64, 'terrain'), (49, 64, 'terrain'), (48, 64, 'terrain'), (49, 59, 'terrain'), (48, 59, 'terrain'), (47, 59, 'terrain'), (51, 58, 'terrain'), (46, 63, 'terrain'), (45, 63, 'terrain'), (44, 63, 'terrain'), (46, 59, 'terrain'), (45, 59, 'terrain'), (44, 59, 'terrain'), (43, 59, 'terrain')]
    ,
    [(58, 45, 'terrain'), (59, 53, 'terrain'), (57, 53, 'terrain'), (56, 50, 'terrain'), (54, 52, 'terrain'), (54, 54, 'terrain'), (58, 56, 'terrain'), (58, 58, 'terrain'), (58, 60, 'terrain'), (52, 56, 'terrain'), (52, 58, 'terrain'), (52, 60, 'terrain'), (51, 51, 'terrain'), (51, 49, 'terrain'), (53, 47, 'terrain'), (55, 47, 'terrain'), (56, 44, 'terrain'), (54, 44, 'terrain'), (52, 44, 'terrain'), (50, 44, 'terrain'), (48, 44, 'terrain'), (48, 46, 'terrain'), (48, 48, 'terrain'), (48, 50, 'terrain'), (46, 52, 'terrain'), (46, 54, 'terrain'), (46, 56, 'terrain'), (46, 58, 'terrain'), (46, 60, 'terrain'), (46, 62, 'terrain'), (47, 44, 'hazard'), (47, 46, 'hazard'), (56, 56, 'terrain'), (59, 64, 'terrain'), (57, 64, 'terrain'), (53, 64, 'terrain'), (46, 64, 'terrain'), (55, 63, 'terrain'), (55, 59, 'terrain'), (55, 61, 'terrain'), (47, 48, 'hazard'), (51, 64, 'terrain'), (58, 49, 'terrain'), (58, 47, 'terrain'), (49, 53, 'terrain'), (49, 55, 'terrain'), (49, 57, 'terrain'), (49, 59, 'terrain'), (49, 61, 'terrain'), (49, 63, 'terrain'), (54, 50, 'terrain'), (51, 47, 'terrain'), (51, 53, 'terrain'), (46, 50, 'terrain')]
    ,
    [(58, 45, 'terrain'), (56, 46, 'terrain'), (55, 46, 'terrain'), (52, 47, 'terrain'), (51, 47, 'terrain'), (53, 47, 'terrain'), (50, 47, 'terrain'), (48, 48, 'terrain'), (47, 48, 'terrain'), (46, 48, 'terrain'), (45, 49, 'terrain'), (45, 50, 'terrain'), (45, 51, 'terrain'), (41, 58, 'hazard'), (42, 59, 'hazard'), (44, 59, 'hazard'), (46, 60, 'hazard'), (48, 60, 'hazard'), (49, 61, 'hazard'), (51, 61, 'hazard'), (58, 76, 'terrain'), (58, 77, 'terrain'), (58, 78, 'terrain'), (57, 62, 'terrain'), (57, 63, 'terrain'), (57, 64, 'terrain'), 
    (51, 65, 'hazard'), (53, 67, 'hazard'), (53, 69, 'hazard'), (51, 71, 'hazard'), (60, 66, 'hazard'), (60, 68, 'hazard'), (60, 70, 'hazard'), (60, 72, 'hazard'), (60, 74, 'hazard'), (60, 64, 'hazard'), (60, 62, 'hazard'), (60, 60, 'hazard'), (60, 58, 'hazard'), (60, 56, 'hazard'), (60, 54, 'hazard'), (52, 66, 'hazard'), (52, 70, 'hazard'), (53, 68, 'hazard'), (50, 61, 'hazard'), (47, 60, 'hazard'), (45, 59, 'hazard'), (43, 59, 'hazard')]
    ,
    [(59, 55, 'hazard'), (58, 56, 'hazard'), (57, 56, 'hazard'), (56, 56, 'hazard'), (55, 56, 'hazard'), (53, 56, 'hazard'), (54, 56, 'hazard'), (54, 55, 'terrain'), (55, 55, 'terrain'), (56, 55, 'terrain'), (57, 55, 'terrain'), (52, 55, 'hazard'), (49, 48, 'terrain'), (50, 48, 'terrain'), (51, 48, 'terrain'), (52, 48, 'terrain'), (54, 48, 'hazard'), (53, 47, 'hazard'), (52, 47, 'hazard'), (51, 47, 'hazard'), (50, 47, 'hazard'), (49, 47, 'hazard'), (48, 47, 'hazard'), (47, 48, 'hazard'), (55, 49, 'hazard'), (60, 54, 'hazard'), (49, 57, 'terrain'), (49, 58, 'terrain'), (49, 59, 'terrain'), (49, 60, 'terrain'), (50, 57, 'hazard'), (50, 58, 'hazard'), (50, 59, 'hazard'), (50, 60, 'hazard'), (49, 62, 'hazard'), (50, 61, 'hazard'), (50, 56, 'hazard'), (49, 55, 'hazard')]

    ]

    app.chunkDict['hard'] = [

    [(60, 49, 'terrain'), (59, 49, 'terrain'), (58, 49, 'terrain'), (57, 49, 'terrain'), (56, 49, 'terrain'), (55, 49, 'terrain'), (54, 49, 'terrain'), (53, 49, 'terrain'), (46, 59, 'terrain'), (48, 59, 'terrain'), (49, 59, 'terrain'), (50, 59, 'terrain'), (51, 59, 'terrain'), 
    (52, 59, 'terrain'), (47, 59, 'terrain'), (46, 58, 'hazard'), (46, 56, 'hazard'), (53, 48, 'terrain'), (53, 50, 'terrain'), (50, 67, 'hazard'), (52, 67, 'hazard'), (54, 67, 'hazard'), (56, 67, 'hazard'), (58, 67, 'hazard'), (60, 67, 'hazard')]
    ,
    [(60, 50, 'terrain'), (59, 50, 'terrain'), (58, 50, 'terrain'), (53, 50, 'terrain'), (54, 50, 'terrain'), (57, 50, 'terrain'), (56, 50, 'terrain'), (55, 50, 'terrain'), (53, 49, 'terrain'), (53, 48, 'terrain'), (51, 59, 'terrain'), (52, 59, 'terrain'), (53, 59, 'terrain'), 
    (53, 62, 'terrain'), (53, 63, 'terrain'), (53, 60, 'terrain'), (53, 61, 'terrain'), (53, 64, 'terrain'), (53, 65, 'terrain'), (45, 65, 'terrain'), (46, 65, 'terrain'), (47, 65, 'terrain'), (48, 65, 'terrain'), (49, 65, 'terrain'), (45, 66, 'terrain'), (45, 64, 'hazard'), (45, 63, 'hazard'), (45, 62, 'hazard'), (39, 72, 'terrain'), (40, 72, 'terrain'), (41, 73, 'hazard'), (43, 73, 'hazard'), (45, 73, 'hazard'), (47, 73, 'hazard'), (49, 73, 'hazard'), (51, 73, 'hazard'), (53, 73, 'hazard'), (59, 73, 'hazard'), (55, 73, 'hazard'), (57, 73, 'hazard'), (39, 73, 'terrain'), (40, 73, 'terrain'), (35, 76, 'terrain'), (36, 76, 'terrain'), (37, 76, 'terrain'), (38, 76, 'terrain'), (34, 74, 'hazard'), (34, 75, 'hazard'), (34, 76, 'hazard'), (34, 73, 'hazard'), (39, 76, 'hazard'), (41, 76, 'hazard'), (43, 76, 'hazard'), (45, 76, 'hazard'), (47, 76, 'hazard'), (51, 76, 'hazard'), (49, 76, 'hazard'), (53, 76, 'hazard')]
    ,
    [(57, 50, 'terrain'), (55, 58, 'terrain'), (53, 66, 'terrain'), (48, 71, 'terrain'), (45, 64, 'terrain'), (40, 59, 'terrain'), (37, 69, 'terrain'), (37, 83, 'terrain'), (38, 83, 'hazard'), (40, 83, 'hazard'), (44, 83, 'hazard'), (50, 83, 'hazard'), (52, 83, 'hazard'), (54, 
    83, 'hazard'), (56, 83, 'hazard'), (60, 83, 'hazard'), (58, 83, 'hazard'), (48, 83, 'hazard'), (46, 83, 'hazard'), (42, 83, 'hazard')]
    ,
    [(60, 48, 'terrain'), (58, 49, 'terrain'), (57, 50, 'terrain'), (59, 49, 'terrain'), (58, 51, 'terrain'), (59, 51, 'terrain'), (60, 53, 'hazard'), (60, 55, 'hazard'), (60, 57, 'hazard'), (60, 59, 'hazard'), (60, 61, 'hazard'), (60, 63, 'hazard'), (58, 68, 'terrain'), (59, 68, 'terrain'), (57, 69, 'terrain'), (60, 65, 'hazard'), (60, 67, 'hazard'), (58, 70, 'terrain'), (59, 70, 'terrain'), (60, 71, 'terrain'), (60, 51, 'terrain')]
    ,
    [(56, 57, 'terrain'), (57, 57, 'terrain'), (55, 57, 'terrain'), (48, 58, 'terrain'), (49, 58, 'terrain'), (50, 58, 'terrain'), (51, 58, 'terrain'), (50, 57, 'hazard'), (56, 58, 'hazard'), (57, 58, 'hazard'), (49, 57, 'hazard'), (42, 55, 'terrain'), (43, 55, 'terrain'), (44, 55, 'terrain'), (45, 55, 'terrain'), (43, 56, 'hazard'), (44, 56, 'hazard'), (40, 60, 'terrain'), (36, 60, 'terrain'), (37, 60, 'terrain'), (38, 60, 'terrain'), (39, 60, 'terrain'), (39, 59, 'hazard'), (38, 59, 'hazard'), (37, 59, 'hazard'), (60, 73, 'hazard'), (58, 73, 'hazard'), (54, 73, 'hazard'), (52, 73, 'hazard'), (44, 73, 'hazard'), (46, 73, 'hazard'), (56, 73, 'hazard'), (50, 73, 'hazard'), (48, 73, 'hazard')]
    ,
    [(59, 63, 'terrain'), (58, 63, 'terrain'), (57, 63, 'terrain'), (60, 63, 'terrain'), (56, 63, 'terrain'), (52, 62, 'terrain'), (51, 62, 'terrain'), (53, 62, 'terrain'), (55, 63, 'terrain'), (54, 63, 'terrain'), (50, 62, 'terrain'), (49, 62, 'terrain'), (48, 61, 'terrain'), 
    (47, 61, 'terrain'), (46, 61, 'terrain'), (45, 61, 'terrain'), (44, 61, 'terrain'), (43, 60, 'terrain'), (42, 60, 'terrain'), (41, 60, 'terrain'), (39, 59, 'terrain'), (38, 59, 'terrain'), (36, 59, 'terrain'), (37, 59, 'terrain'), (35, 58, 'terrain'), (34, 58, 'terrain'), (33, 58, 'terrain'), (32, 58, 'terrain'), (32, 59, 'terrain'), (32, 60, 'terrain'), (33, 61, 'terrain'), (33, 62, 'terrain'), (34, 63, 'terrain'), (35, 64, 'terrain'), (35, 65, 'terrain'), (36, 61, 'terrain'), (37, 61, 'terrain'), (37, 62, 'terrain'), (36, 62, 'terrain'), (37, 67, 'terrain'), (36, 67, 'terrain'), (36, 68, 'terrain'), (37, 68, 'terrain'), (40, 63, 'terrain'), (40, 62, 'terrain'), (40, 66, 'terrain'), (40, 67, 'terrain'), (39, 61, 'terrain'), (39, 68, 'terrain'), (34, 66, 'terrain'), (33, 67, 'terrain'), (33, 68, 'terrain'), (32, 69, 'terrain'), (32, 70, 'terrain'), (32, 71, 'terrain'), (40, 59, 'terrain'), (38, 64, 'hazard'), (38, 65, 'hazard'), (39, 65, 'terrain'), (39, 64, 'terrain')]
    ,
    [(41, 69, 'terrain'), (40, 68, 'terrain'), (40, 67, 'terrain'), (39, 66, 'terrain'), (39, 65, 'terrain'), (39, 64, 'terrain'), (39, 58, 'terrain'), (39, 57, 'terrain'), (39, 56, 'terrain'), (40, 55, 'terrain'), (40, 54, 'terrain'), (41, 53, 'terrain'), (42, 52, 'terrain'), (43, 52, 'terrain'), (44, 51, 'terrain'), (45, 51, 'terrain'), (46, 51, 'terrain'), (47, 50, 'terrain'), (48, 50, 'terrain'), (49, 50, 'terrain'), (50, 50, 'terrain'), (51, 50, 'terrain'), (52, 51, 'terrain'), (53, 51, 'terrain'), (54, 51, 'terrain'), (55, 52, 'terrain'), (56, 52, 'terrain'), (57, 53, 'terrain'), (58, 54, 'terrain'), (58, 55, 'terrain'), (59, 66, 'hazard'), (58, 67, 'hazard'), (57, 69, 'hazard'), (56, 70, 'hazard'), (54, 71, 'hazard'), (48, 72, 'terrain'), (49, 72, 'terrain'), (50, 72, 'terrain'), (51, 72, 'terrain'), (38, 63, 'hazard'), (38, 62, 'hazard'), (38, 61, 'hazard'), (38, 60, 'hazard'), (38, 59, 'hazard'), (60, 64, 'hazard'), (48, 60, 'hazard'), (49, 61, 'hazard'), (48, 62, 'hazard'), (47, 61, 'hazard'), (52, 72, 'hazard'), (48, 73, 'terrain'), (48, 74, 'terrain')]
    ,
    [(57, 51, 'terrain'), (57, 52, 'terrain'), (57, 53, 'terrain'), (56, 54, 'hazard'), (56, 55, 'hazard'), (56, 59, 'hazard'), (57, 60, 'terrain'), (57, 61, 'terrain'), (57, 62, 'terrain'), (57, 63, 'terrain'), (56, 64, 'hazard'), (52, 67, 'terrain'), (53, 67, 'terrain'), (54, 67, 'hazard'), (50, 60, 'terrain'), (45, 55, 'terrain'), (40, 52, 'terrain'), (35, 67, 'terrain'), (36, 67, 'terrain'), (37, 67, 'terrain'), (34, 67, 'hazard'), (33, 67, 'hazard'), (44, 76, 'hazard'), (46, 76, 'hazard'), (48, 76, 'hazard'), (50, 76, 'hazard'), (54, 76, 'hazard'), (56, 76, 'hazard'), (58, 76, 'hazard'), (60, 76, 'hazard'), (52, 76, 'hazard'), (58, 51, 'terrain'), (49, 60, 'terrain'), (49, 59, 'terrain'), (49, 58, 'terrain'), (48, 57, 'hazard'), (51, 67, 'hazard'), (50, 67, 'hazard'), (55, 67, 'hazard')]
    ,
    [(56, 48, 'terrain'), (51, 46, 'terrain'), (51, 47, 'hazard'), (50, 47, 'terrain'), (50, 46, 'terrain'), (50, 48, 'hazard'), (45, 54, 'terrain'), (56, 49, 'terrain'), (57, 49, 'terrain'), (57, 48, 'terrain'), (46, 54, 'terrain'), (46, 55, 'terrain'), (45, 55, 'terrain'), (39, 59, 'terrain'), (40, 59, 'terrain'), (40, 58, 'hazard'), (39, 57, 'hazard'), (39, 58, 'terrain'), (41, 59, 'terrain'), (52, 46, 'terrain'), (38, 68, 'hazard'), (40, 68, 'hazard'), (42, 68, 'hazard'), (44, 68, 'hazard'), (46, 68, 'hazard'), (48, 68, 'hazard'), (56, 68, 'hazard'), (58, 68, 'hazard'), (60, 68, 'hazard'), (50, 68, 'hazard'), (52, 68, 'hazard'), (54, 68, 'hazard')]
    ,
    [(60, 47, 'terrain'), (59, 47, 'terrain'), (58, 47, 'terrain'), (57, 49, 'terrain'), (56, 49, 'terrain'), (55, 49, 'terrain'), (54, 51, 'terrain'), (53, 51, 'terrain'), (52, 51, 'terrain'), (55, 51, 'hazard'), (57, 51, 'hazard'), (59, 51, 'hazard'), (47, 69, 'terrain'), (47, 70, 'terrain'), (50, 61, 'terrain'), (49, 61, 'terrain'), (48, 61, 'terrain'), (47, 61, 'terrain'), (46, 61, 'terrain'), (45, 61, 'hazard'), (44, 61, 'hazard'), (48, 70, 'hazard'), (50, 70, 'hazard'), (52, 70, 'hazard'), (54, 70, 'hazard'), (56, 70, 'hazard'), (58, 70, 'hazard'), (60, 70, 'hazard'), (47, 71, 'terrain'), (47, 72, 'terrain')]
    ,
    [(59, 52, 'terrain'), (57, 52, 'terrain'), (58, 52, 'terrain'), (60, 52, 'terrain'), (56, 52, 'terrain'), (55, 52, 'terrain'), (54, 52, 'terrain'), (53, 52, 'terrain'), (52, 52, 'terrain'), (47, 63, 'terrain'), (48, 63, 'terrain'), (49, 63, 'terrain'), (46, 63, 'terrain'), 
    (45, 63, 'terrain'), (49, 64, 'terrain'), (51, 53, 'terrain'), (51, 54, 'terrain'), (51, 55, 'terrain'), (51, 52, 'terrain'), (51, 56, 'terrain'), (48, 64, 'terrain'), (47, 64, 'terrain'), (46, 64, 'terrain'), (45, 64, 'terrain'), (44, 64, 'terrain'), (43, 64, 'terrain'), (42, 64, 'terrain'), (42, 62, 'hazard'), (43, 62, 'hazard'), (44, 62, 'hazard'), (44, 73, 'hazard'), (46, 73, 'hazard'), (48, 73, 'hazard'), (50, 73, 'hazard'), (52, 73, 'hazard'), (54, 73, 'hazard'), (56, 73, 'hazard'), (58, 73, 'hazard'), (60, 73, 'hazard')]
    ,
    [(60, 47, 'terrain'), (59, 49, 'terrain'), (59, 47, 'terrain'), (58, 47, 'terrain'), (58, 49, 'terrain'), (60, 49, 'terrain'), (52, 58, 'terrain'), (53, 58, 'terrain'), (54, 58, 'terrain'), (57, 49, 'terrain'), (56, 47, 'terrain'), (55, 47, 'terrain'), (55, 48, 'terrain'), (55, 49, 'terrain'), (56, 49, 'terrain'), (57, 47, 'terrain'), (52, 66, 'hazard'), (54, 66, 'hazard'), (56, 66, 'hazard'), (60, 66, 'hazard'), (58, 66, 'hazard'), (54, 59, 'terrain'), (51, 58, 'terrain'), (50, 58, 'terrain'), (49, 58, 'terrain'), (48, 58, 'terrain'), (47, 58, 'terrain'), (46, 58, 'hazard'), (44, 58, 'hazard'), (58, 48, 'hazard'), (60, 48, 'hazard'), (56, 48, 'hazard'), (53, 59, 'terrain'), (52, 59, 'terrain')]
    ,
    [(59, 46, 'terrain'), (60, 46, 'terrain'), (58, 46, 'terrain'), (57, 46, 'terrain'), (56, 46, 'terrain'), (55, 46, 'terrain'), (54, 46, 'terrain'), (53, 46, 'terrain'), (53, 59, 'terrain'), (49, 51, 'hazard'), (51, 51, 'hazard'), (53, 51, 'hazard'), (53, 45, 'terrain'), (60, 78, 'terrain'), (59, 78, 'terrain'), (58, 78, 'terrain'), (54, 78, 'terrain'), (53, 78, 'terrain'), (55, 78, 'terrain'), (56, 78, 'terrain'), (57, 78, 'terrain'), (53, 76, 'terrain'), (53, 77, 'terrain'), (53, 75, 'terrain'), (53, 66, 'hazard'), (51, 66, 'hazard'), (49, 66, 'hazard'), (53, 60, 'terrain'), (54, 60, 'terrain'), (55, 60, 'terrain'), (56, 60, 'terrain'), (57, 60, 'terrain'), (58, 60, 'terrain'), (59, 60, 'terrain'), (60, 60, 'terrain'), (53, 58, 'terrain')]
    ,
    [(55, 51, 'terrain'), (56, 51, 'terrain'), (57, 51, 'terrain'), (51, 44, 'terrain'), (52, 44, 'terrain'), (53, 44, 'terrain'), (54, 51, 'hazard'), (50, 44, 'hazard'), (49, 51, 'terrain'), (49, 52, 'terrain'), (49, 53, 'terrain'), (49, 54, 'terrain'), (47, 57, 'hazard'), (42, 57, 'hazard'), (48, 59, 'hazard'), (50, 61, 'hazard'), (43, 63, 'hazard'), (49, 66, 'hazard'), (52, 63, 'terrain'), (52, 64, 'terrain'), (52, 66, 'terrain'), (52, 67, 'terrain'), (52, 68, 'terrain'), (52, 69, 'terrain'), (52, 65, 'terrain'), (53, 70, 'hazard'), (55, 70, 'hazard'), (57, 70, 'hazard'), (59, 70, 'hazard'), (52, 70, 'terrain')]
    ,
    [(60, 56, 'terrain'), (59, 56, 'terrain'), (58, 56, 'terrain'), (57, 56, 'terrain'), (56, 56, 'terrain'), (55, 56, 'terrain'), (54, 56, 'terrain'), (53, 56, 'terrain'), (52, 56, 'terrain'), (51, 56, 'terrain'), (50, 56, 'terrain'), (49, 56, 'terrain'), (57, 53, 'hazard'), (55, 53, 'hazard'), (53, 53, 'hazard'), (48, 56, 'hazard'), (46, 56, 'hazard'), (44, 56, 'hazard'), (42, 56, 'hazard'), (52, 53, 'terrain'), (51, 53, 'terrain'), (50, 53, 'terrain'), (49, 53, 'terrain'), (48, 53, 'terrain'), (47, 53, 'terrain'), (46, 53, 'terrain'), (45, 53, 'terrain'), (44, 53, 'terrain'), (43, 53, 'terrain'), (42, 53, 'terrain'), (37, 63, 'hazard'), (39, 63, 'hazard'), (41, 63, 'hazard'), (43, 63, 'hazard'), (45, 63, 'hazard'), (47, 63, 'hazard'), (49, 63, 'hazard'), (51, 63, 'hazard'), (52, 58, 'hazard'), (51, 57, 'hazard'), (52, 62, 'hazard')]
    ,
    [(56, 49, 'terrain'), (55, 49, 'terrain'), (54, 49, 'terrain'), (54, 50, 'terrain'), (54, 51, 'terrain'), (60, 60, 'hazard'), (52, 60, 'hazard'), (57, 60, 'hazard'), (49, 60, 'hazard'), (60, 68, 'terrain'), (58, 68, 'terrain'), (54, 68, 'terrain'), (52, 68, 'terrain'), (48, 68, 'terrain'), (46, 68, 'terrain'), (43, 60, 'hazard'), (42, 60, 'hazard'), (41, 60, 'hazard'), (44, 60, 'hazard'), (48, 58, 'terrain'), (48, 57, 'terrain'), (48, 56, 'terrain'), (48, 55, 'terrain'), (48, 54, 'terrain'), (48, 53, 'hazard'), (44, 53, 'terrain'), (39, 53, 'terrain'), (39, 54, 'terrain'), (44, 68, 'hazard'), (56, 68, 'terrain'), (50, 68, 'terrain'), (58, 60, 'hazard'), (59, 60, 'hazard'), (50, 60, 'hazard'), (51, 60, 'hazard'), (38, 55, 'terrain'), (38, 56, 'terrain')]
    ,
    [(56, 51, 'terrain'), (51, 50, 'terrain'), (51, 51, 'terrain'), (51, 52, 'terrain'), (46, 54, 'terrain'), (46, 53, 'terrain'), (46, 52, 'terrain'), (46, 51, 'terrain'), (46, 50, 'terrain'), (46, 49, 'terrain'), (46, 48, 'terrain'), (40, 62, 'terrain'), (41, 62, 'terrain'), 
    (42, 62, 'terrain'), (43, 62, 'terrain'), (38, 62, 'terrain'), (39, 62, 'terrain'), (43, 70, 'hazard'), (37, 62, 'hazard'), (36, 62, 'hazard'), (45, 69, 'hazard'), (47, 68, 'hazard'), (49, 67, 'hazard'), (51, 66, 'hazard'), (53, 65, 'hazard'), (55, 64, 'hazard'), (57, 63, 'hazard'), (59, 62, 'hazard')]
    ,
    [(56, 58, 'terrain'), (55, 58, 'terrain'), (54, 58, 'terrain'), (53, 58, 'terrain'), (52, 58, 'terrain'), (51, 56, 'terrain'), (50, 56, 'terrain'), (49, 56, 'terrain'), (48, 56, 'terrain'), (47, 55, 'terrain'), (47, 54, 'terrain'), (47, 53, 'terrain'), (46, 53, 'terrain'), (45, 53, 'terrain'), (51, 57, 'terrain'), (57, 59, 'terrain'), (58, 59, 'terrain'), (59, 59, 'terrain'), (60, 59, 'terrain'), (44, 55, 'terrain'), (44, 54, 'terrain'), (44, 56, 'terrain'), (45, 57, 'terrain'), (45, 58, 'terrain'), (46, 59, 'terrain')]
    ,
    [(60, 47, 'terrain'), (57, 47, 'terrain'), (55, 47, 'terrain'), (54, 47, 'terrain'), (59, 47, 'terrain'), (53, 48, 'terrain'), (57, 49, 'terrain'), (59, 49, 'terrain'), (60, 49, 'terrain'), (56, 47, 'terrain'), (58, 47, 'terrain'), (58, 49, 'terrain'), (55, 49, 'terrain'), 
    (54, 49, 'terrain'), (53, 49, 'terrain'), (53, 47, 'terrain'), (56, 49, 'terrain'), (49, 58, 'terrain'), (49, 59, 'terrain'), (50, 58, 'terrain'), (43, 70, 'terrain'), (44, 70, 'terrain'), (45, 70, 'terrain'), (46, 70, 'terrain'), (42, 70, 'hazard'), (41, 70, 'hazard'), (48, 77, 'terrain'), (48, 78, 'terrain'), (48, 79, 'terrain'), (48, 80, 'terrain'), (49, 80, 'hazard'), (51, 80, 'hazard'), (53, 80, 'hazard'), (55, 80, 'hazard'), (57, 80, 'hazard'), (59, 80, 'hazard'), (43, 71, 'hazard'), (44, 71, 'hazard'), (45, 71, 'hazard')]
    ,
    [(57, 50, 'terrain'), (58, 50, 'terrain'), (58, 51, 'terrain'), (54, 50, 'terrain'), (53, 50, 'terrain'), (53, 51, 'terrain'), (58, 54, 'terrain'), (57, 55, 'terrain'), (58, 55, 'terrain'), (54, 55, 'terrain'), (53, 55, 'terrain'), (53, 54, 'terrain'), (49, 59, 'terrain'), (48, 60, 'terrain'), (47, 60, 'terrain'), (46, 61, 'terrain'), (38, 57, 'terrain'), (39, 58, 'terrain'), (40, 58, 'terrain'), (41, 58, 'terrain'), (33, 62, 'terrain'), (34, 62, 'terrain'), (34, 63, 'terrain'), (30, 62, 'terrain'), (29, 62, 'terrain'), (29, 63, 'terrain'), (29, 66, 'terrain'), (29, 67, 'terrain'), (30, 67, 'terrain'), (33, 67, 'terrain'), (34, 67, 'terrain'), (34, 66, 'terrain'), (54, 85, 'terrain'), (54, 84, 'terrain'), (54, 83, 'terrain'), (54, 86, 'terrain'), (54, 82, 'terrain'), (54, 81, 'terrain'), (55, 85, 'hazard'), (57, 85, 'hazard'), (59, 85, 'hazard'), (25, 72, 'hazard'), (27, 72, 'hazard'), (29, 72, 'hazard'), (31, 72, 'hazard'), (33, 72, 'hazard'), (35, 72, 'hazard'), (37, 72, 'hazard'), (39, 72, 'hazard'), (41, 72, 'hazard'), (43, 72, 'hazard'), (45, 72, 'hazard'), (47, 72, 'hazard'), (45, 62, 'terrain'), (44, 65, 'hazard'), (42, 65, 'hazard')]

    ]

    ### Buttons ###
    app.buttons = dict()
    app.buttonProperties = list()
    createButton(app)
    

    app.editModes = ['Add', 'Remove']
    app.editModesIndex = 0
    app.editAssignedMode = app.editModes[app.editModesIndex]

    app.difficultyButtons = list()
    difficultyButtonsSetup(app)
    ### Chunk generation ###
    app.startEasy = 0               # These three starting values don't change.
    app.startNormal = 1/3 * 100
    app.startHard = 2/3 * 100

    app.startingMu = None # This gets rewritten when chunks are generated based on the gameDifficulty
    app.sigma = 15 # The standard deviation amount. The larger the value, the more likely adjacent difficulty chunks are selected --> the wider the bellcurve about the startingMu
    # The lower the value, the skinnier the bellcurve is

    app.wallX = -300
    app.wallXVel = 2
    app.pseudoCol = app.wallX / 10
    app.gameOver = False

    app.image1 = app.loadImage('synth2.jpg')
    app.image1 = ImageTk.PhotoImage(app.image1)
    app.songList = ['what we fight for.wav', '347 midnight demons.wav', 'hangem all.wav',
    'roller mobster.wav', 'le perv.wav', 'youre mine.wav']
    app.prevSong = None
    app.song = None
    app.randomSongTitle = random.choice(app.songList)
    app.songLength = 0
    app.startTime = 0
    app.play_obj = None
    if songsEnabled == True:
        app.radioEnable = True
        radio(app)
    else:
        app.radioEnable = False


### RADIO SYNTH ### 
### ALL CREDITS TO THE 15-112 TAs WHO GAVE THE AUDIO MODULE LECTURE!!!###
### ALL CREDITS TO THE 15-112 TAs WHO GAVE THE AUDIO MODULE LECTURE!!!###
### ALL CREDITS TO THE 15-112 TAs WHO GAVE THE AUDIO MODULE LECTURE!!!###
def getSound(AudioFile):
    return AudioSegment.from_file(AudioFile) # import via pydub

def playSound(sound):
    rawAudioData = sound.raw_data
    np_array = np.frombuffer(rawAudioData, dtype=np.int16)
    wave_obj = sa.WaveObject(np_array, 2, 2, 48000)
    return wave_obj.play()

def lengthSound(sound):
    return sound.duration_seconds

def makeSound5Second(sound):
    return sound[:5000]

def radio(app):
    if app.radioEnable == True:
        app.startTime = time.time()
        while app.randomSongTitle == app.prevSong: # so the last song isn't played again
            app.randomSongTitle = random.choice(app.songList)
        app.prevSong = app.randomSongTitle

        app.song = getSound(app.randomSongTitle)
        #app.song = makeSound5Second(app.song) # debug purposes
        app.songLength = lengthSound(app.song)
        app.play_obj = playSound(app.song)



####################


def timerFired(app):
    
    if app.gameOver == False:
        app.p.updatePos()
        app.p.gravity()
        # checkCollision(app) # comment out when XCollision and YCollision are written

        if abs(app.p.xVel) > 0: # to replace checkCollision
            checkTouchWall(app)
        if abs(app.p.yVel) > 0:
            checkTouchFloor(app)
        

        playerRow, playerCol = getCell(app, app.p.x, app.p.y)
        if app.p.xVel > 0:
            for endCol in app.endCols:
                if playerCol == endCol + 5:
                    if playerRow < 50:
                        app.p.completeChunk()
                    

        if playerCol > app.colHighScore  % 128 :
            app.colHighScore = 128 * app.screensCrossed + playerCol
        
        if playerCol >= 128:
            app.screensCrossed += 1
            initializeGameMode(app)
    
        if app.mode == 'gameMode':
            pseudoPlayerCol = app.screensCrossed * 128 + playerCol
            colSeparation = pseudoPlayerCol - app.pseudoCol
            if colSeparation < 80 and colSeparation > 32: # if the wall is very close to the player:
                app.wallXVel = 2
            elif colSeparation < 32:
                app.wallXVel = 1.5
            elif colSeparation > 200:
                app.wallXVel = 4 # speed up if player is very far ahead
            else:
                app.wallXVel = 2.5 # slow down if in the zone

            app.wallX += app.wallXVel
            app.pseudoCol = app.wallX / 10
                # app.colHighScore = 0
                # app.screensCrossed = 0
            if colSeparation <= 0:
                gameOver(app)

            if (app.screensCrossed < app.pseudoCol/128) and (app.pseudoCol/128 < app.screensCrossed + 1):
                row, col = 0, app.pseudoCol % 128
                for block in app.terrain:
                    if block.col <= col:
                        app.terrain.remove(block)
    if songsEnabled == True:
        if time.time() - app.startTime >= app.songLength + 2: # continuously play songs
            app.play_obj.stop()
            radio(app)
        
def gameOver(app):
    app.gameOver = True


def getCell(app, x, y):
    gridWidth = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows

    row = int((y-app.margin)//cellHeight)
    col = int((x-app.margin)//cellWidth)
    return row, col


def keyPressed(app, event):

    if songsEnabled == True:
        if event.key == 'n':
            app.play_obj.stop()
            radio(app)
        if event.key == 'd':
            if app.radioEnable == True:
                app.radioEnable = False
                app.play_obj.stop()
            else:
                app.radioEnable = True
                app.play_obj.stop()
                radio(app)

    if app.mode == 'editorMode': # updates assigned difficulty in editor
        if event.key == 'c': # clear board:
            app.terrain = []
        if event.key == 'w':
            if app.diffIndex > 0:
                app.diffIndex -= 1
            elif app.diffIndex == 0:
                app.diffIndex = len(app.difficulties) - 1
            app.chunkAssignedDifficulty = app.difficulties[app.diffIndex]
        if event.key == 's': 
            if app.diffIndex < len(app.difficulties) - 1:
                app.diffIndex += 1
            elif app.diffIndex == len(app.difficulties) - 1:
                app.diffIndex = 0
            app.chunkAssignedDifficulty = app.difficulties[app.diffIndex]
        
        if event.key == 'W':
            if app.blockTypesIndex > 0:
                app.blockTypesIndex -= 1
            elif app.blockTypesIndex == 0:
                app.blockTypesIndex = len(app.blockTypes) - 1
            app.blockAssignedType = app.blockTypes[app.blockTypesIndex]
        if event.key == 'S': 
            if app.blockTypesIndex < len(app.blockTypes) - 1:
                app.blockTypesIndex += 1
            elif app.blockTypesIndex == len(app.blockTypes) - 1:
                app.blockTypesIndex = 0
            app.blockAssignedType = app.blockTypes[app.blockTypesIndex]

        if event.key == 'Space':
            app.editModesIndex = not app.editModesIndex # toggles between place and remove blocks
            app.editAssignedMode = app.editModes[app.editModesIndex]



        if event.key == 'x': # export
            # if app.terrain not in app.chunkDict[app.chunkAssignedDifficulty] and 
            if app.terrain != []:
                chunk = []
                for object in app.terrain:
                    row = object.row
                    col = object.col
                    type = object.type
                    block = (row, col, type)
                    # print(f'Block = {block}')
                    chunk.append(block)
                app.chunkDict[app.chunkAssignedDifficulty].append(chunk)

            app.terrain = [] # reset terrain after exporting
            
        if event.key == 'l': # load for debug purposes
            app.terrain = []
            if app.chunkDict[app.chunkAssignedDifficulty] != []:
                chunk = random.choice(app.chunkDict[app.chunkAssignedDifficulty])
                for block in chunk:
                    row = block[0]
                    col = block[1]
                    type = block[2] # hazard, terrain, trampoline, etc. implement later
                    newTerrain = Terrain(row, col, type)
                    app.terrain.append(newTerrain)

        
    ### PLAYER MOVEMENT ###
    if app.gameOver == False:
        if event.key == "Right":
            app.p.xVel = 5
        if event.key == "Left":
            app.p.xVel = -5
        if event.key == "Up" or event.key == 'z':
            app.p.jump()
        if event.key == "Down":
            app.p.xVel = 0


    ### DEBUG INPUTS ###
    '''
    if event.key == 'p': # debug purposes, list all
        print()
        for block in app.terrain:
            print(block.row, block.col)
    if event.key == 'P':
        print(app.chunkDict)
    if event.key == 'r': # debug, remove all placed terrain
        app.terrain = []
    if event.key == 'u':
        if app.terrain != []:
            app.terrain.pop()
    '''
    

            

def mousePressed(app, event): # Toggles between ON and OFF
    if app.mode == 'gameMode':
        x0, y0, x1, y1 = app.buttons['startScreenMode'] # return to title screen button
        if x0 < event.x and event.x < x1:
            if y0 < event.y and event.y < y1:
                # button was pressed
                app.mode = 'startScreenMode'
                app.terrain = []
                app.gameOver = False

    if app.mode == "editorMode":
        row, col = getCell(app, event.x, event.y)
        newTerrain = Terrain(row, col, app.blockAssignedType)
        didRemove = False
        blockThere = False

        # the screen is 128 blocks across, want chunks to be at most 128/3 = 43 wide
        if 43 <= col and col <= 86 and row <= 60:
            if app.editAssignedMode == 'Add':
                for block in app.terrain:
                    if newTerrain == block:
                        blockThere = True
                if blockThere == False:
                    app.terrain.append(newTerrain)
                    
            elif app.editAssignedMode == 'Remove':
                for block in app.terrain:
                    if newTerrain == block:
                        app.terrain.remove(newTerrain)


        x0, y0, x1, y1 = app.buttons['startScreenMode'] # return to title screen button
        if x0 < event.x and event.x < x1:
            if y0 < event.y and event.y < y1:
                # button was pressed
                app.mode = 'startScreenMode'
                app.terrain = []

    
    if app.mode == 'startScreenMode':
        for key in app.buttons:
            x0, y0, x1, y1 = app.buttons[key]
            if x0 < event.x and event.x < x1:
                if y0 < event.y and event.y < y1:
                    # button was pressed
                    if key == 'gameMode':
                        app.wallX = -800
                        app.wallXVel = 2
                        app.pseudoCol = app.wallX / 10
                        app.colHighScore = 0
                        app.screensCrossed = 0
                        initializeGameMode(app)
                    app.mode = key

        for i in range(len(app.difficultyButtons)):
            x0, y0, x1, y1 = app.difficultyButtons[i]
            if x0 < event.x and event.x < x1:
                if y0 < event.y and event.y < y1:
                    # button was pressed
                    if i == 0:
                        app.gameDiffIndex = 0
                        
                    if i == 1:
                        app.gameDiffIndex = 1
                    if i == 2:
                        app.gameDiffIndex = 2
                    app.gameDifficulty = app.gameDifficulties[app.gameDiffIndex]

                    
    
    if app.mode == 'aboutMode':
        x0, y0, x1, y1 = app.buttons['startScreenMode'] # return to title screen button
        if x0 < event.x and event.x < x1:
            if y0 < event.y and event.y < y1:
                # button was pressed
                app.mode = 'startScreenMode'
                app.terrain = []
    
'''
When generating, if the value falls into one of these ranges:
easy : [0, 1/3 * 100)
normal: [1/3 * 100, 2/3 * 100)
hard: [2/3 * 100, 100]

select a random level from that set of chunks

if a value is < 0:, set value to 0; if value > 100: set value to 100

startEasy --> mu = 0 # mu is average value
startNormal --> mu = 1/3 * 100
startHard --> mu = 2/3 * 100

standard deviation: 34
'''
def selectChunkDiff(app):
    

    # app.gameDifficulty = 'normal' (initially)
    
    if app.gameDifficulty == 'easy': app.startingMu = app.startEasy         # 00
    elif app.gameDifficulty == 'normal': app.startingMu = app.startNormal   # 33
    elif app.gameDifficulty == 'hard': app.startingMu = app.startHard       # 66
    

    # Per one screen crossed, player has travelled 3-4 chunks 
    # use math.log so that increasing gains don't 
    muFactor = 15
    if app.screensCrossed >= 1:
        app.startingMu += math.log(app.screensCrossed) * muFactor

    
    

    x = random.normalvariate(app.startingMu, app.sigma) # the value generated in the bellCurve
    if x > 100: x = 100
    if x < 0: x = 0

    if 0 <= x and x < 1/3 * 100:
        chunkDifficulty = 'easy'
    elif 1/3 * 100 <= x and x < 2/3 * 100:
        chunkDifficulty = 'normal'
    elif 2/3 * 100 <= x and x <= 100:
        chunkDifficulty = 'hard'
    return chunkDifficulty
    


def initializeGameMode(app): # TO BE CONTINUED
    app.terrain = []
    app.p.x = 10
    chunkSpace = 10 # manual amount of space between last block of previous chunk, and first block of next chunk
    spawnChunk = 10 # how far away the chunks should begin spawning
    usedEasyIndexes = []
    usedNormalIndexes = []
    usedHardIndexes = []
    

    '''
    (app.endCols is the list of starting columns of chunks generated)
    Pseudo code for how the player moves through chunks:
    The maximum amount of columns the screen can fit at any one time is 1280/10 = 128
    SO, if the nth chunk has a starting position nCol that is > 128, only generate chunks up to the (n-1)th chunk
    eg. app.endCols = [20, 55, 76, 122, 157...] --> since the 5th chunk begins at 157, the 4th chunk ends at 157 
    (or 147, subtracting chunk space) therefore that 4th chunk should not be drawn until the player gets past the 3rd chunk

    in summary, generate chunks as long as they end before col 128, in batches of the possible amounts. When the player reaches col 128,
    re-generate chunks, reset player position to startSpawn, keeping track of the player's pseudo col number 
    (for high score and difficulty determination purposes) in the same batch format, such that the chunks end before col 128.
    '''

    chunkDifficulties =  []
    for i in range(10): # no chance of there ever being more than 10 chunks per screen
        newChunkDifficulty = selectChunkDiff(app)
        chunkDifficulties.append(newChunkDifficulty)
    # Now I have a list of 10 difficulties generated with the bell curve:
    # ['normal', 'normal', 'easy', 'normal', 'easy', 'hard', 'normal', 'normal', 'easy', 'normal']

    app.endCols = [0]
    highestAdjCol = 0

    for i in range(len(chunkDifficulties)):
        thisChunkDifficulty = chunkDifficulties[i] # --> ['normal', 'normal', 'easy', 'normal', 'easy', 'hard', 'normal', 'normal', 'easy', 'normal']
        randomIndex = random.randrange(len(app.chunkDict[thisChunkDifficulty])) # choose a random chunk from the dictionary key of the thisChunkDifficulty

        if thisChunkDifficulty == 'easy':
            while randomIndex in usedEasyIndexes:
                randomIndex = random.randrange(len(app.chunkDict[thisChunkDifficulty]))
            usedEasyIndexes.append(randomIndex)
        if thisChunkDifficulty == 'normal':
            while randomIndex in usedNormalIndexes:
                randomIndex = random.randrange(len(app.chunkDict[thisChunkDifficulty]))
            usedNormalIndexes.append(randomIndex)
        if thisChunkDifficulty == 'hard':
            while randomIndex in usedHardIndexes:
                randomIndex = random.randrange(len(app.chunkDict[thisChunkDifficulty]))
            usedHardIndexes.append(randomIndex)
        
        chunk = app.chunkDict[thisChunkDifficulty][randomIndex]
        lowestCol = None
        highestCol = None
        endCol = None

        for block in chunk:
            row, col, type = block[0], block[1], block[2]
            if lowestCol == None or col < lowestCol:
                lowestCol = col
            elif highestCol == None or col > highestCol:
                highestCol = col
        chunkWidth = highestCol - lowestCol 

            

        if i == 0:
            endCol = highestCol - lowestCol + spawnChunk
            if endCol < 128:

                for block in chunk:
                    row, col, type = block[0], block[1], block[2]
                    col -= lowestCol # now all columns are set relative to 0
                    col += spawnChunk
                        
                    newTerrain = Terrain(row, col, type)
                    app.terrain.append(newTerrain)
                app.endCols.append(endCol)
                highestAdjCol = chunkWidth + chunkSpace # adjusted furthest block

        else:
            endCol = highestCol - lowestCol + spawnChunk + highestAdjCol
            if endCol < 128:
                for block in chunk:
                    row, col, type = block[0], block[1], block[2]
                    col -= lowestCol
                    col += spawnChunk
                    col += highestAdjCol
                            
                    newTerrain = Terrain(row, col, type)
                    app.terrain.append(newTerrain)
                    
                app.endCols.append(endCol)
                highestAdjCol += chunkWidth + chunkSpace # adjusted furthest block



    

def mouseDragged(app, event):
    if app.mode == "editorMode":
        row, col = getCell(app, event.x, event.y)
        newTerrain = Terrain(row, col, app.blockAssignedType)
        didRemove = False
        blockThere = False

        # the screen is 128 blocks across, want chunks to be at most 128/3 = 43 wide
        if 43 <= col and col <= 86 and row <= 60:
            if app.editAssignedMode == 'Add':
                for block in app.terrain:
                    if newTerrain == block:
                        blockThere = True
                if blockThere == False:
                    app.terrain.append(newTerrain)
                    
            elif app.editAssignedMode == 'Remove':
                for block in app.terrain:
                    if newTerrain == block:
                        app.terrain.remove(newTerrain)
                   


def getCellBounds(app, row, col):
    gridWidth = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows

    x0 = app.margin + cellWidth * col 
    x1 = x0 + cellWidth
    y0 = app.margin + cellHeight * row
    y1 = y0 + cellHeight

    # if app.mode == 'gameMode':
    #     x0 -= app.p.x
    #     x1 -= app.p.x
    return x0, y0, x1, y1


def drawGrid(app, canvas):
    for block in app.terrain:
        x0, y0, x1, y1 = getCellBounds(app, block.row, block.col)
        canvas.create_rectangle(x0, y0, x1, y1, fill = block.fill, outline = block.outline)

def drawPlayer(app, canvas):
    if app.gameOver == False:
        x0, y0, x1, y1 = (app.p.x-app.p.r, app.p.y-app.p.r,
                        app.p.x+app.p.r, app.p.y+app.p.r)
        canvas.create_rectangle(x0, y0, x1, y1, fill = app.p.fill, outline = app.p.outline)


### DEBUG FUNCTION ###
def drawStats(app, canvas):
    offset = 5
    playerRow, playerCol = getCell(app, app.p.x, app.p.y)
    pseudoPlayerCol = app.screensCrossed * 128 + playerCol
    colSeparation = int(pseudoPlayerCol - app.pseudoCol)

    if app.mode == 'gameMode':
        canvas.create_text(offset, 5, text = f'The Wall is {colSeparation} blocks behind you!',
            font = 'Times 12 bold', anchor = 'nw', fill = cyan)



def createButton(app):
    x = app.width / 2
    y = app.height * 5 / 8
    color = 'cyan'
    offset = app.height / 8

    width = app.width / 4
    height = app.height / 10
    
    for i in range(3): # primary buttons
        if i == 0:
            text = 'Play game!'
            mode = 'gameMode'

        if i == 1:
            text = 'Editor'
            mode = 'editorMode'
        if i == 2:
            text = 'About the game'
            mode = 'aboutMode'

        x0, y0, x1, y1 = ((x-width/2), (y-height/2), (x+width/2), (y+height/2))
        curProperties = (x0, y0, x1, y1, color, text, mode)
        app.buttonProperties.append(curProperties)
        app.buttons[mode] = x0, y0, x1, y1
        y += offset
    
    # return button that shows while in the editorMode and aboutMode
    reWidth = 100
    reHeight = 40
    offset = 30
    cx = app.width - 4 * offset
    cy = app.height - 2 * offset
    x0, y0, x1, y1 = cx - reWidth/2, cy - reHeight/2, cx + reWidth, cy + reHeight
    text = 'Return to title'
    mode = 'startScreenMode'
    curProperties = (x0, y0, x1, y1, color, text, mode)
    app.buttonProperties.append(curProperties)
    app.buttons[mode] = x0, y0, x1, y1


def difficultyButtonsSetup(app):
    for i in range(3): # buttons to select gameDifficulty
        buttonHeight = 40
        buttonWidth = 150
        buttonVertSpace = 0
        totalHeight = (buttonHeight + buttonVertSpace) * 3 - buttonVertSpace

        initialHeight = (app.height - totalHeight) / 1.6

        
        if i == 0:
            color = 'lightGreen'
            text = 'Easy'
            x0, y0 = 0, initialHeight
            x1, y1 = x0 + buttonWidth, y0 + buttonHeight
            app.difficultyButtons.append([x0, y0, x1, y1])
            
        if i == 1:
            color = 'lightYellow'
            text = 'Normal'
            x0, y0 = 0, initialHeight + buttonVertSpace + buttonHeight
            x1, y1 = x0 + buttonWidth, y0 + buttonHeight
            app.difficultyButtons.append([x0, y0, x1, y1])
            
        if i == 2:
            color = 'pink'
            text = 'Hard'
            x0, y0 = 0, initialHeight + buttonVertSpace * 2 + buttonHeight * 2
            x1, y1 = x0 + buttonWidth, y0 + buttonHeight
            app.difficultyButtons.append([x0, y0, x1, y1])
            

def startScreenMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = '#0D0241')
    title = 'ad Infinitum : you can </not> advance'
    titleFont = 'Times 40 bold'
    titleWidth = app.width / 2
    titleHeight = app.height / 10
    titleFill = '#1de2f6'
    # the square behind the title
    canvas.create_rectangle(app.width/2 - titleWidth, app.height/4 - titleHeight, 
        app.width/2 + titleWidth, app.height / 4 + titleHeight, 
        fill = '#261447', width = 3, outline = 'magenta')

    # the title text
    canvas.create_text(app.width / 2, app.height / 4,
        text = title, font = titleFont, fill = titleFill, activefill = '#ff3864')


    font = 'Times 16 bold'

    for i in range(len(app.buttonProperties) - 1):
        # curProperties = (x0, y0, x1, y1, color, text, mode)
        b = app.buttonProperties[i]
        x0, y0, x1, y1, color, text = (b[0], b[1], b[2], b[3], 
            b[4], b[5])
        x = (x0 + x1) / 2
        y = (y0 + y1) / 2
            
        canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 2,
            activefill = '#ff3864')
        canvas.create_text(x, y, text = text, font = 'Times 14 bold', state = 'disabled')


    
    for i in range(len(app.difficultyButtons)):
        x0, y0, x1, y1 = app.difficultyButtons[i]
        x = (x0 + x1) / 2
        y = (y0 + y1) / 2

        if i == 0:
            text = 'Easy'
            fill = '#ffd319'
            if app.gameDifficulty == 'easy':
                font = 'Times 14 bold'
            else:
                font = 'Times 14'
            canvas.create_text(x, y0, text = "Select difficulty",
                font = 'Times 14 bold', anchor = 's', fill = '#1de2f6')
                
        if i == 1:
            text = 'Normal'
            fill = '#ff901f'            
            if app.gameDifficulty == 'normal':
                font = 'Times 14 bold'
            else:
                font = 'Times 14'
                
                
        if i == 2:
            text = 'Hard'
            fill = '#ff2975'            
            if app.gameDifficulty == 'hard':
                font = 'Times 14 bold'
            else:
                font = 'Times 14'



        canvas.create_rectangle(x0, y0, x1, y1, fill = fill, activefill = 'white', outline = 'black', width = 1)
        canvas.create_text(x, y, text = text, font = font, state = 'disabled')
            



    ### My name in the corner :) ###
    canvas.create_text(app.width - 15, app.height - 5, text = 'Game by Josiah Miggiani',
        font = 'Times 12', anchor = 'se', fill = cyan)


def drawGameOver(app, canvas):
    playerRow, playerCol = getCell(app, app.p.x, app.p.y)

    pseudoPlayerCol = app.screensCrossed * 128 + playerCol

    x = app.width/2
    y = app.height/2
    halfWidth = 300
    halfHeight = 150
    # canvas.create_rectangle(x- halfWidth, y - halfHeight, x + halfWidth, y + halfHeight,
    #     fill = blue)
    canvas.create_text(x, y - app.height/6, text = 'GAME OVER', font = 'Times 80 bold',
        fill = cyan)
    canvas.create_text(x, y, text = f'You advanced {pseudoPlayerCol} blocks!', 
        font = 'Times 20 bold', fill = cyan)

    
    
def drawGround(app, canvas):
    canvas.create_rectangle(0, app.p.groundLvl + app.p.r, app.width, 
        app.height, fill = '#090019') # dirt
    canvas.create_rectangle(0, app.p.groundLvl + app.p.r, app.width,
        app.p.groundLvl + 2 * app.p.r, fill = black, outline = cyan,
        width = 1) # grass

def drawBackground(app, canvas):
    if bgImageEnabled:
        canvas.create_image(app.width/2, app.height/2, image=app.image1)
    else:
        canvas.create_rectangle(0,0, app.width, app.height, fill = '#000000')

        colWidth = 80
        numCols = int(app.width/colWidth) + 1
        rowHeight = colWidth
        numRows = int(app.height/rowHeight) + 1
        for i in range(numCols):
            canvas.create_line(colWidth*i, 0, colWidth*i, app.height, fill = fuschia1, width = 1)
        for i in range(numRows):
            canvas.create_line(0, rowHeight*i, app.width, rowHeight*i, fill = fuschia1, width = 1)
        
        sunColors = [yellow, orange, salmon, redSalmon, cyan]
        sunIndex = 0
        multiplier = 1
        r = 100
        cx, cy = app.width/2, app.p.groundLvl 
        for i in range(len(sunColors)):
            canvas.create_oval(cx - r, cy -r, cx + r, cy + r, fill = sunColors[sunIndex], outline = sunColors[sunIndex])
            r -= 10 * multiplier
            
            sunIndex += 1
            multiplier += 0.6
        
    #canvas.create_rectangle(0, 0, app.width, app.height, fill = abyss)



def gameMode_redrawAll(app, canvas):
    
    # visual representation of the ground. Doesn't actually affect
        # app.p.yVel or app.p.y
    #canvas.create_rectangle(0, 0, app.width, app.height, fill = 'lightBlue')
    drawBackground(app, canvas)
    drawGround(app, canvas)

    for endCol in app.endCols:
        x0, y0, x1, y1 = getCellBounds(app, 61, endCol + 3)
        canvas.create_rectangle(x0, y0, x1, y1, fill = 'pink')
    
    drawGrid(app, canvas)
    drawPlayer(app, canvas)

    drawStats(app, canvas)
    

    ### Draw return to main menu button ###
    b = app.buttonProperties[3]
    x0, y0, x1, y1, color, text = (b[0], b[1], b[2], b[3], 
    b[4], b[5])
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
        
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 2,
        activefill = 'white')
    canvas.create_text(x, y, text = text, font = 'Times 14 bold', state = 'disabled')

    if (app.screensCrossed < app.pseudoCol/128) and (app.pseudoCol/128 < app.screensCrossed + 1): # DRAW THE WALL HERE!!
        row, col = 0, app.pseudoCol % 128
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        xDif = x1 - x0
        x0 = x1 - xDif * 2
        y1 = app.height
        canvas.create_rectangle(x0, y0, x1, y1, fill = black, outline = fuschia2)
        
    if app.gameOver == True:
            drawGameOver(app, canvas)

def editorMode_drawInstructions(app, canvas):
    # drawBackground(app, canvas)
    canvas.create_rectangle(0,0, app.width, app.height, fill = '#0D0241')
    canvas.create_rectangle(0, 0, 430, app.height, fill = abyss)
    # stipple = 'gray25'
    # stipples are resource intensive. do not use when drawing the player
    canvas.create_rectangle(870, 0, app.width, app.height, fill = abyss)
    drawGround(app, canvas)

    topText = ("- Click and drag with mouse1 to place blocks\n- Adjust assigned difficulty with 'w' and 's'  " + 
        "\n- Press 'x' to export chunk to assigned difficulty \n- Adjust block type using " +
        "Shift + 'W' and Shift + 'S' " + "\n- Press 'c' to clear board \n- Press 'l' to load a random " + 
        "chunk from the \n      selected difficulty \n- Lastly, press the spacebar to toggle " + 
        "between \n      adding and removing blocks")
    canvas.create_text(5, 5, anchor = 'nw', font = 'Times 14 bold', 
        width = app.width * 2 / 3, text = topText, fill = cyan)


    ### DIFFICULTY ASSIGNMENT ###
    r = 30
    for i in range(3):
        if i == 0: 
            fill = '#ffd319'
            text = 'Easy' # easy
        if i == 1: 
            fill = '#ff901f' 
            text = 'Normal' # normal
        if i == 2: 
            fill = '#ff2975' 
            text = 'Hard' # hard

        x0, y0, x1, y1 = app.width - 75, i * r, app.width, r + i*r
        center = ( (x1 + x0) / 2, (y1 + y0) / 2 )
        canvas.create_rectangle(x0, y0, x1, y1, fill = fill)
        canvas.create_text(center[0], center[1], text = text,
            font = 'Times 12', fill = 'black')

    # draw triangle
    # then shift so it points to current difficulty assignment
    if app.chunkAssignedDifficulty == 'easy': shift, arrow = 0, '#ffd319'
    elif app.chunkAssignedDifficulty == 'normal': shift, arrow = r, '#ff901f'
    elif app.chunkAssignedDifficulty == 'hard': shift, arrow = r*2, '#ff2975'

    canvas.create_polygon(x0-r, 0 + shift, x0-r, r + shift, x0, r/2 + shift,
        fill = arrow, outline = 'black')

    ### BLOCK TYPES ###
    for i in range(len(app.blockTypes)): # currently only goes through i = 0, 1
        if i == 0:
            fill = '#540d6e'
            text = 'Terrain'
        if i == 1:
            fill = '#fd1d53'
            text = 'Hazard'
        
        x2, y2, x3, y3 = (app.width - 75, (5 * r) + i * r, app.width,
            (6 * r) + i*r)
        center = ( (x3 + x2) / 2, (y3 + y2) / 2 )
        canvas.create_rectangle(x2, y2, x3, y3, fill = fill)
        canvas.create_text(center[0], center[1], text = text,
            font = 'Times 12', fill = 'white')
        
    # draw triangle
    # then shift so it points to current difficulty assignment
    if app.blockAssignedType == 'terrain': shift, arrow = 0, '#540d6e'
    if app.blockAssignedType == 'hazard': shift, arrow = r, '#fd1d53'

    startY = (5 * r)
    canvas.create_polygon(x2-r, startY + shift, x2-r, startY + r + shift, 
        x2, startY + r/2 + shift, fill = arrow, outline = 'black')

    
    ### ADD OR REMOVE BLOCKS ###
    y4, y5 = y2 + 2*r, y3 + 2*r
    newCenter = ( (x3 + x2)/2, (y5 + y4)/2)
    if app.editAssignedMode == 'Add':
        fill = 'White'
        textColor = 'Black'
    elif app.editAssignedMode == 'Remove':
        fill = 'Black'
        textColor = 'White'
    canvas.create_rectangle(x2, y4, x3, y5,
        fill = fill)
    canvas.create_text(newCenter[0], newCenter[1], 
        text = (f'{app.editAssignedMode}'), fill = textColor, font = 'Times 12')


def editorMode_redrawAll(app, canvas):
    #canvas.create_rectangle(0, 0, app.width, app.height, fill = 'yellow',
    #    stipple = 'gray12')
    editorMode_drawInstructions(app, canvas)

    drawGrid(app, canvas)
    drawPlayer(app, canvas)

    drawStats(app, canvas)

    ### Draw return to main menu button ###
    b = app.buttonProperties[3]
    x0, y0, x1, y1, color, text = (b[0], b[1], b[2], b[3], 
    b[4], b[5])
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
        
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 2,
        activefill = 'white')
    canvas.create_text(x, y, text = text, font = 'Times 14 bold', state = 'disabled')


def aboutMode_redrawAll(app, canvas):
    titleWidth = app.width / 2
    titleHeight = app.height / 10
    fill = '#1de2f6'
    canvas.create_rectangle(0, 0, app.width, app.height, fill = '#0D0241')
    canvas.create_rectangle(app.width/2 - titleWidth, app.height/4 - titleHeight, 
        app.width/2 + titleWidth, app.height / 4 + titleHeight, 
        fill = '#261447', width = 3, outline = 'magenta')
    canvas.create_text(app.width/2, app.height / 4,
        text = 'About: ad Infinitum', font = 'Times 40 bold', fill = fill)
    canvas.create_text(app.width/2, app.height / 4 + 130,
        text = 'Movement mechanics are awesome. \n This game is in dedication to Celeste, and countless other incredible games.',
        font = 'Times 20 bold', fill = fill, justify = 'center' )

    theGame = ("In ad Infinitum, levels are procedurally generated, and get progressively harder the further you go. \nYour goal is to advance as far as possible before the wall reaches you!")
    canvas.create_text(app.width/2, app.height*4.5/8,
        text = theGame, font = 'Times 14 bold', justify = 'center', fill = fill)
    aboutBlurb = ("Controls: Use the arrow keys to move. The down arrow key stops your horizontal velocity, allowing for precise control. \n This game features a 'pseudo' double-jump, which ties in with wall-jumping. You can jump at any time, so long as your jump is preserved. \n " +
        "By running off a ledge, rather than jumping off, you do not expend your jump, allowing you to jump in mid-air. \n There are two ways to gain back your jump: landing back on the ground, or hitting a wall as you're falling. This is how you wall-jump!" +
        "\n \nPress 'n' to skip to the next song in the radio, and 'd' to toggle the radio on and off.")
    canvas.create_text(app.width/2, app.height*5.75/8,
        text = aboutBlurb, font = 'Times 12 bold', justify = 'center',
            fill = fill)
    
    otherBlurb = ("Audio code copied from the 15-112 Audio Module lecture given by the TAs. \nBackground image from RoyaltyFreeTube via Creative Commons. \nAll featured music by Carpenter Brut.")
    canvas.create_text(app.width/2, app.height*7/8,
        text = otherBlurb, font = 'Times 12 bold', justify = 'center',
            fill = fill)
    

    ### Draw return to main menu button ###
    b = app.buttonProperties[3]
    x0, y0, x1, y1, color, text = (b[0], b[1], b[2], b[3], 
    b[4], b[5])
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
        
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 2,
        activefill = 'white')
    canvas.create_text(x, y, text = text, font = 'Times 14 bold', state = 'disabled')

def drawRadio(app, canvas):
    x = 10
    y = app.height - 14
    xr, yr = 5, 3
    canvas.create_oval(x-xr, y-yr, x+xr, y+yr, fill = cyan)
    canvas.create_line(x+xr-1, y, x+xr+2, y - 15, fill = cyan, width = 1)
    canvas.create_line(x+xr+2, y-15, x+xr+5, y-10, fill = cyan, width = 1)
    if app.randomSongTitle == 'what we fight for.wav': title = 'What We Fight For'
    if app.randomSongTitle == '347 midnight demons.wav': title = '347 Midnight Demons'
    if app.randomSongTitle == 'hangem all.wav': title = "Hang'em All"
    if app.randomSongTitle == 'roller mobster.wav': title = 'Roller Mobster'
    if app.randomSongTitle == 'le perv.wav': title = 'Le Perv'
    if app.randomSongTitle == 'youre mine.wav': title = "You're Mine"

    if app.radioEnable == False:
        canvas.create_text(25, app.height - 5, text = f"Radio disabled",
            font = 'Times 12', fill = cyan, anchor = 'sw')
    else:    
        canvas.create_text(25, app.height - 5, text = f'Now playing: Carpenter Brut - {title}',
            font = 'Times 12', fill = cyan, anchor = 'sw')
    


def redrawAll(app, canvas):
    if app.mode == "startScreenMode":
        startScreenMode_redrawAll(app, canvas)
    elif app.mode == "gameMode":
        gameMode_redrawAll(app, canvas)
    elif app.mode == "editorMode":
        editorMode_redrawAll(app, canvas)
    elif app.mode == 'aboutMode':
        aboutMode_redrawAll(app, canvas)
    drawRadio(app, canvas)





runApp(width=1280, height=720)