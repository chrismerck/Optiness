#!/usr/bin/env python2

"""
A skeleton class for an Optiness pathfinder
Darren Alton
"""

class Brain:
	name = 'unnamed solver'

	def __init__(self, game, args = {}, defaultargs = {}):
		self.game = game
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
		self.args = args

	# Note: this should 'yield' pygame surfaces throughout execution,
	#       but it's acceptable to just 'return' a 1-tuple when finished.
	#       if no screen change was made, return None to skip updating the display
	def Step(self):
		for i in self.game.ValidInputs():
			self.game.Input(i)
		return (self.game.Draw(),)

	# true iff a winning path has been found
	def Victory(self):
		return self.game.Victory()

	# return the list of input states from start to goal
	def Path(self):
		return []

	# handle events from pygame, if relevant
	def Event(self, evt):
		pass

	# return the screen (width, height) that should be used
	def ScreenSize(self):
		return self.game.ScreenSize()


LoadedBrain = Brain
