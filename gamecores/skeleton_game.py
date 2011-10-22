#!/usr/bin/env python2

"""
A skeleton class for an Optiness gamecore
Darren Alton
"""

import pygame
from cPickle import dumps, loads

xmax = 100 # width of the screen
ymax = 80  # height of the screen

class Game:
	name = 'skeleton game'

	def __init__(self):
		pass

	# return a copy of the "screen" for visualization
	def Draw(self):
		ret = pygame.surface.Surface((xmax, ymax))
		ret.fill((0,123,45))
		return ret

	# return true if the game has reached a goal state
	def Victory(self):
		return True

	# under-or-equal-estimate of input-frames to goal
	def Heuristic(self):
		return 0

	# return some copy of the game's state
	def Freeze(self):
		return dumps(self.__dict__)

	# restore a saved state returned by Freeze
	def Thaw(self, state):
		self.__dict__ = loads(state)

	# set the state of the "control pad" and run a frame
	def Input(self, data):
		pass

	# must return an iterable of all possible inputs
	def ValidInputs(self):
		return [0]

LoadedGame = Game
