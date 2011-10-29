#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses a greedy algorithm with low memory costs
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'lookahead': 4 }

class Wario(Brain):
	name = 'wario'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.lookahead = self.args['lookahead']
		self.input_substrings = []
		self._GenInputLists()

		self.current_state = self.game.Freeze()
		self.current_heur = self.game.Heuristic()
		self.input_log = []
		self.terminated = False

	def _GenInputLists(self, path = []):
		if len(path) >= self.lookahead:
			self.input_substrings.append(path)
		else:
			for i in self.game.ValidInputs():
				self._GenInputLists(path + [i])

	def Step(self):
		new_best = None
		start_state = self.current_state

		for i in self.input_substrings:
			if self.terminated:  break
			self.game.Thaw(start_state)
			for j in i:  self.game.Input(j)

			h = self.game.Heuristic()
			if h < self.current_heur:
				new_best = i
				self.current_heur = h
				self.current_state = self.game.Freeze()
			yield self.game.Draw()

		if new_best is None:
			print 'Wario: got stuck in a local minimum or was unable to make visible progress.'
			self.terminated = True
		else:
			self.input_log += new_best

	def Event(self, evt):
		if evt.type == pygame.QUIT:  self.terminated = True

	def Victory(self):
		return self.game.Victory() or self.terminated

	def Path(self):
		return self.input_log

LoadedBrain = Wario
