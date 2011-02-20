


"""
A Simple Maze Game written in Python
Chris Merck

Object: To reach the right-hand side of the screen.
"""

import pygame
import random

xmax = 100
ymax = 80
scale = 10
pxmax = xmax*scale
pymax = ymax*scale

screen = pygame.display.set_mode((pxmax,pymax))
running = 1

wall_color = (180,85,20)
floor_color = (0,0,0)

# tile types:
floor = 0
wall = 1

# directions
up = (0,-1)
down = (0,1)
left = (-1,0)
right = (1,0)

# base-pairs 
A = up
T = down
G = left
C = right

def MakeWorld(seed):

	# God does not play dice
	random.seed(seed)

	# all wall tiles at first
	world = [[wall for i in range(ymax)] for j in range(xmax)]

	# start on left side in the middle
	x = 0
	y = ymax/2

	world[x][y]=floor

    # wander around until we hit the right side
	t = 0
	while True:
		if random.randint(0,1)==1:
			step = 1
		else:
			step = -1

		if random.randint(0,1)==1:
			x+=step
		else:
			y+=step

		if x<0:
			x=0
		if y<0:
			y=0
		if x==xmax:
			x=xmax-1
			return world
		if y==ymax:
			y=ymax-1


		world[x][y]=floor
		t+=1



def DrawWorld(world):
	for x in range(xmax):
		for y in range(ymax):
			if world[x][y] == wall:
				color = wall_color
			else:
				color = floor_color
			rect = pygame.Rect(x*scale,y*scale,scale,scale)
			pygame.draw.rect(screen,color,rect)


world = MakeWorld(1)

while running:
	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		running=0
	#screen.fill((0,0,0))
	DrawWorld(world)
	pygame.display.flip()


