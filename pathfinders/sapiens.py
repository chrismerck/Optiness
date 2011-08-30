#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses human input
Darren Alton
"""

import pygame

supported_games = [ 'maze', 'snes' ]

class Brain:
	name = 'sapiens'

	def __init__(self, game): # any arguments besides "game" must have defaults
		gname = game.__class__.name
		if gname not in supported_games:
			raise Exception('solver "%s" does not play game "%s"' % (name, gname))

		self.game = game

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

