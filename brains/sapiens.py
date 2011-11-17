#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses human input
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'fps': 60, # run at 60fps because we have a human watching
                'joynum': 0,
				'keyhat': 'wsad',
				'keybuttons': 'klji1056' }

class Sapiens(Brain):
	name = 'sapiens'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.fps = self.args['fps']
		self.clock = pygame.time.Clock()

		pygame.joystick.init()
		joynum = self.args['joynum']
		if joynum >= 0:
			self.joy = pygame.joystick.Joystick(joynum)
			self.joy.init()
			print 'Sapiens:', self.joy.get_name()

		self.input_log = []
		self.input_map = game.HumanInputs()
		self.pad = 0
		self.won = False

		UDLR = ('up', 'down', 'left', 'right')

		map = self.input_map
		self.hat_reset = 0
		for i in UDLR:
			str = 'hat0_{}'.format(i)
			if str in map:  self.hat_reset |= map[str]
		self.hat_reset = ~self.hat_reset
		self.hat_lut = [ { -1: 'left', 1:  'right' },
			             { 1:  'up',   -1: 'down' } ]

		self.key_map = {}
		keyhat = self.args['keyhat']
		for i in xrange(len(keyhat)):
			str = 'hat0_{}'.format(UDLR[i])
			self.key_map[ord(keyhat[i])] = map[str]
		keybuttons = self.args['keybuttons']
		for i in xrange(len(keybuttons)):
			self.key_map[ord(keybuttons[i])] = map[i]

	def Step(self):
		self.clock.tick(self.fps)
		self.game.Input(self.pad)
		self.input_log.append(self.pad)
		pygame.display.set_caption('{}'.format(self.game.Heuristic()))
		if self.game.Victory() and not self.won:
			self.won = True
			print 'Sapiens: you won the game!'
		return (self.game.Draw(),)

	def Event(self, evt):
		map = self.input_map
		kmap = self.key_map
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
		elif evt.type == pygame.KEYDOWN:
			if evt.key in kmap:  self.pad |= kmap[evt.key]
		elif evt.type == pygame.KEYUP:
			if evt.key in kmap:  self.pad &= ~kmap[evt.key]

	def Path(self):
		return self.input_log

	def Victory(self):
		return False

LoadedBrain = Sapiens
