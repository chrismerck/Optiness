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

	def Draw(self): # return a copy of the "screen" for visualization
		ret = pygame.surface.Surface((xmax, ymax))
		ret.fill((0,123,45))
		return ret

	def Victory(self):
		return True

	def Freeze(self): # return some copy of the game's state
		return dumps(self.__dict__)

	def Thaw(self, state): # restore a saved state returned by Freeze
		self.__dict__ = loads(state)

	def Input(self, data): # set the state of the "control pad" and run a frame
		pass

	def ValidInputs(self):
		return []

LoadedGame = Game
