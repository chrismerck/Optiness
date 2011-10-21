#!/usr/bin/env python2

"""
An Optiness "pathfinder" that plays back recorded input
Darren Alton
"""

import pygame
import cPickle

from skeleton_solver import Brain

class Rerun(Brain):
	name = 'rerun'

	def __init__(self, game):
		self.supported_games = [ 'maze', 'snes' ]
		Brain.__init__(self, game)

		self.clock = pygame.time.Clock()
		self.inputstring = cPickle.load(open('inputstring.pickle', 'r'))
		self.outputstring = []

	def Step(self):
		self.clock.tick(60) # run at 60fps because we have a human watching
		frameinput = 0
		if len(self.inputstring): frameinput = self.inputstring.pop(0)
		self.game.Input(frameinput)
		self.outputstring.append(frameinput)
		return (self.game.Draw(),)

	def Path(self):
		return self.outputstring

LoadedBrain = Rerun
