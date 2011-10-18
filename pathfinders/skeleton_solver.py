#!/usr/bin/env python2

"""
A skeleton class for an Optiness pathfinder
Darren Alton
"""

class Brain:
	name = 'skeleton solver'

	def __init__(self, game): # any arguments besides "game" must have defaults
		gname = game.__class__.name
		if gname not in self.supported_games:
			raise Exception('solver "%s" does not play game "%s"' % (name, gname))
		self.game = game

	def Step(self): # any arguments must have defaults
		pass

LoadedBrain = Brain
