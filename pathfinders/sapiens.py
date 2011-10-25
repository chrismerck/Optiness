#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses human input
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = {}

class Sapiens(Brain):
	name = 'sapiens'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		pygame.joystick.init()
		self.joy = pygame.joystick.Joystick(0)
		self.joy.init()
		print self.joy.get_name()

		self.input_log = []
		self.input_map = game.HumanInputs()
		self.pad = 0

		map = self.input_map
		self.hat_reset = 0
		for i in ('up', 'down', 'left', 'right'):
			str = 'hat0_{}'.format(i)
			if str in map:  self.hat_reset |= map[str]
		self.hat_reset = ~self.hat_reset
		self.hat_lut = [ { -1: 'left', 1:  'right' },
			             { 1:  'up',   -1: 'down' } ]


	def Step(self):
		self.game.Input(self.pad)
		self.input_log.append(self.pad)
		return (self.game.Draw(),)

	def Event(self, evt):
		map = self.input_map
		if evt.type == pygame.JOYHATMOTION:
			hat = evt.value
			lut = self.hat_lut
			self.pad &= self.hat_reset
			for i in (0,1):
				if hat[i] in lut[i]:
					str = 'hat0_{}'.format( lut[i][hat[i]] )
					if str in map:  self.pad |= map[str]
		elif evt.type == pygame.JOYBUTTONDOWN:
			if evt.button in map:  self.pad |= map[evt.button]
		elif evt.type == pygame.JOYBUTTONUP:
			if evt.button in map:  self.pad &= ~map[evt.button]

	def Path(self):
		return self.input_log

	def Victory(self):
		return False

LoadedBrain = Sapiens
