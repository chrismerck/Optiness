#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses iterative deepening DFS
Darren Alton
"""

import pygame

from skeleton_solver import Brain

class Inception(Brain):
	name = 'inception'

	def __init__(self, game, depthfactor = 1):
		self.supported_games = [ 'maze', 'snes' ]
		Brain.__init__(self, game)
		self.depthfactor = depthfactor
		self.maxdepth = depthfactor
		self.input_log = None
		self.init_state = game.Freeze()

	def Step(self):
		print 'DFS with max depth', self.maxdepth
		sol = self._DFS(self.init_state)
		if sol is not None:
			self.input_log = sol
		self.maxdepth += self.depthfactor

	def _DFS(self, node, depth = 0):
		for i in self.game.ValidInputs():
			game.Thaw(node)
			game.Input(i)
			if self.game.Victory(): return [i]
			if depth < self.maxdepth:
				ret = self._DFS(game.Freeze(), depth+1)
				if ret is not None:
					ret.insert(0, i)
					return ret
		return None

	def Path(self):
		return self.input_log

LoadedBrain = Inception
