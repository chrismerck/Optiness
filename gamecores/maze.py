#!/usr/bin/env python2

"""
A Simple Maze Game written in Python
Chris Merck

Object: To reach the right-hand side of the screen.
"""

import pygame
import random

from skeleton_game import Game

xmax = 100
ymax = 80
scale = 4

wall_color = (180,85,20)
floor_color = (0,0,0)
player_color = (200,200,200)

# tile types:
floor = 0
wall = 1


# Maze game
class Maze(Game):
	name = 'maze'

	def __init__(self, args = {'seed': 1}):
		Game.__init__(self, args)
		random.seed(args['seed'])  # God does not play dice

		# all wall tiles at first
		self.world = [[wall for i in xrange(ymax)] for j in xrange(xmax)]

		# generating the surface as we go along too
		self.surf = pygame.Surface((xmax,ymax))
		self.surf.fill(wall_color)

		x, y = (1, ymax/2)              # start on left side in the middle

		# create our "Player"
		self.xpos = x
		self.ypos = y

		# carve out the world
		self.world[x][y]=floor                # place the floor tile, thereby demolishing the walls
		self.surf.set_at((x,y), floor_color)  # do the same thing in the visual map

		# wander around until we hit the right side,
		#  but leave a border of wall around the outside
		while x < xmax-1:
			step = random.randint(0,1)*2 - 1

			if random.randint(0,1) == 1:
				x+=step
			else:
				y+=step

			# avoid crossing boundaries, except the right side
			#  (if we hit the right edge, we're done!)
			if y == 0: y=1
			elif y == ymax-1: y=ymax-2
			if x == 0: x=1
			# we check for x out of the right side in the 'while' condition.

			self.world[x][y] = floor
			self.surf.set_at((x,y), floor_color)


	def Draw(self):
		ret = self.surf.copy()
		ret.set_at((self.xpos, self.ypos), player_color)
		return ret

	def Heuristic(self):
		return xmax - self.xpos - 1

	def Input(self, n):
		# directions
		# up, down, left, right = ( (0,-1), (0,1), (-1,0), (1,0) )

		nx = self.xpos
		ny = self.ypos
		vel = ((n&1)*2) - 1 # either +1 or -1

		# either vertical or horizontal
		if n&2:  nx += vel
		else:    ny += vel

		# if we didn't run into a wall or out of bounds, that's our new position
		if nx < xmax and self.world[nx][ny] == floor:
			self.xpos = nx
			self.ypos = ny

	def ValidInputs(self):
		return xrange(4)

	def Freeze(self):
		return (self.xpos, self.ypos)

	def Thaw(self, data):
		self.xpos, self.ypos = data

	def Victory(self):
		return self.xpos >= xmax - 1


LoadedGame = Maze
