#!/usr/bin/env python2

"""
A skeleton class for an Optiness gamecore
Darren Alton
"""

import pygame
from cPickle import dumps, loads
from array import array

xmax = 320 # fallback width of the screen
ymax = 200 # fallback height of the screen

class Game:
	name = 'unnamed game'

	def __init__(self, args={}, defaultargs={}, validargs={}):
		# try to convert args to appropriate types (from str)
		for i in args:
			try:
				args[i] = eval(args[i], {"__builtins__":None}, {})
			except:
				pass

		# load default values for any keys not given
		for i in defaultargs:
			if i not in args:
				args[i] = defaultargs[i]

		# check validargs
		invalids = []
		for i in args:
			if i in validargs:
				validator = validargs[i]
				try:
					iterator = iter(validator)
				except TypeError:
					if hasattr(validator, '__call__'):
						if not validator(args[i]):
							invalids.append(i)
				else:
					if args[i] not in validator:
						print validator
						invalids.append(i)
		if len(invalids):
			for i in invalids:
				print 'invalid value for {}: {}'.format(i, args[i])
			raise Exception('bad arguments provided to game.')

		# otherwise, we're all good...
		self.args = args

	# return a copy of the "screen" for visualization
	def Draw(self):
		ret = pygame.surface.Surface((xmax, ymax))
		ret.fill((0,123,45))
		return ret

	# return true if the game has reached a goal state
	def Victory(self):
		return self.Heuristic() <= 0

	# return true if the game has reached a 'dead' state
	def Defeat(self):
		return self.Heuristic() == float('inf')

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

	# return a dict of button mappings to input bitmasks
	def HumanInputs(self):
		return { 0: 0 }

	# return the screen (width, height) that should be used
	def ScreenSize(self):
		if 'screen' in self.args:  return self.args['screen']
		return (xmax, ymax)

	# return left and right channel, 16-bit sound
	def Sound(self):
		return (0,0)

LoadedGame = Game
