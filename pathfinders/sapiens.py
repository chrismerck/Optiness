#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses human input
Darren Alton
"""

import pygame

from skeleton_solver import Brain

class Sapiens(Brain):
	name = 'sapiens'

	def __init__(self, game):
		self.supported_games = [ 'maze', 'snes' ]
		Brain.__init__(self, game)

		pygame.joystick.init()
		self.joy = pygame.joystick.Joystick(0)
		self.joy.init()
		print self.joy.get_name()

	def Step(self): # any arguments must have defaults
		return self.game.Draw()

	def Event(self, evt):
		if evt.type == pygame.JOYHATMOTION:
			hat = evt.value
			inp = -1
			if hat[1] == 1: inp = 0
			elif hat[1] == -1: inp = 1
			elif hat[0] == -1: inp = 2
			elif hat[0] == 1: inp = 3
			if inp >= 0: self.game.Input(inp)

LoadedBrain = Sapiens
