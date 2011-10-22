#!/usr/bin/env python2

"""
A skeleton class for an Optiness pathfinder
Darren Alton
"""

class Brain:
	name = 'skeleton solver'

	def __init__(self, game):
		gname = game.__class__.name
		if gname not in self.supported_games:
			raise Exception('solver "%s" does not play game "%s"' % (name, gname))
		self.game = game

	def Step(self):
		for i in self.game.ValidInputs():
			self.game.Input(i)
		return (self.game.Draw(),)

	def Victory(self):
		return self.game.Victory()

	def Path(self):
		return []

	def Event(self, evt):
		pass

LoadedBrain = Brain
