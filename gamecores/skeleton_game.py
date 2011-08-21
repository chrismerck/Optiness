#!/usr/bin/env python2

"""
A skeleton class for an Optiness gamecore
Darren Alton
"""

import pygame

xmax = 100 # width of the screen
ymax = 80  # height of the screen

class Game:
	name = 'skeleton game'

	def __init__(self, foo = 1): # must have defaults for any arguments here
		pass

	def Draw(self): # return a copy of the "screen" for visualization
		ret = pygame.surface.Surface((xmax, ymax))
		ret.fill((0,123,246))
		return ret

# TODO: get, restore state.  to be used by the solver.


