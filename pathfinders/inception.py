#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses iterative deepening DFS
Darren Alton
"""

import pygame

from skeleton_solver import Brain

class Inception(Brain):
	name = 'just the tip'

	def __init__(self, game, depthfactor = 1):
		self.supported_games = [ 'maze', 'snes' ]
		Brain.__init__(self, game)

	def Step(self):
		pass  # derp

LoadedBrain = Inception
