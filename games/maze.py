#!/usr/bin/env python2

"""
A Simple Maze Game written in Python
Chris Merck

Object: To reach the right-hand side of the screen.
"""

import pygame
import random

from skeleton_game import Game

wall_color = (180,85,20)
floor_color = (0,0,0)
player_color = (200,200,200)

# tile types:
floor = 0
wall = 1

defaultargs = {	'seed':   1,
				'screen': (100, 80) }

validargs = { 'screen':  lambda x: (len(x) == 2) and (x[0] > 0) and (x[1] > 0) }

# Maze game
class Maze(Game):
	name = 'maze'

	def __init__(self, args = {}):
		Game.__init__(self, args, defaultargs, validargs)
		if 'seed' in self.args:  random.seed(self.args['seed'])  # God does not play dice

		self.inputs = { 'hat0_up':    0b0001,
						'hat0_down':  0b0010,
						'hat0_left':  0b0100,
						'hat0_right': 0b1000 }

		xmax, ymax = self.args['screen']
		self.w, self.h = (xmax, ymax)

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
		return self.w - self.xpos

	def Input(self, n):
		if n == 0:  return

		nx = self.xpos
		ny = self.ypos
		if n & 0b0011: # vertical
			if n & 0b0001: ny -= 1 # up
			else:          ny += 1 # down
		else: # horizontal
			if n & 0b0100: nx -= 1 # left
			else:          nx += 1 # right

		# if we didn't run into a wall or out of bounds, that's our new position
		if nx < self.w and self.world[nx][ny] == floor:
			self.xpos = nx
			self.ypos = ny

	def HumanInputs(self):
		return self.inputs

	def ValidInputs(self):
		return self.inputs.values()

	def Freeze(self):
		return (self.xpos, self.ypos)

	def Thaw(self, data):
		self.xpos, self.ypos = data

	def Victory(self):
		return self.xpos >= self.w - 1



LoadedGame = Maze
