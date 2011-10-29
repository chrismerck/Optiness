#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses a greedy algorithm with low memory costs
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'lookahead':    3,
				'escapedepth':  5 }

class Wario(Brain):
	name = 'wario'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.lookahead = self.args['lookahead']
		self.escapedepth = self.args['escapedepth']

		self.input_log = []
		self.new_best = None
		self.terminated = False

		self._GenInputLists(self.lookahead)

		self.current_state = self.game.Freeze()
		self.current_heur = self.game.Heuristic()
		self.escape_heur = self.current_heur


	def _GenInputLists(self, max, path = []):
		if len(path) == 0:
			self.input_substrings = []
		else:
			self.input_substrings.append(path)
		if len(path) < max:
			for i in self.game.ValidInputs():
				self._GenInputLists(max, path + [i])

	def _RunString(self, instring):
		for j in instring:  self.game.Input(j)
		h = self.game.Heuristic()
		if h < self.current_heur:
			self.new_best = instring
			self.current_heur = h
			self.current_state = self.game.Freeze()
			return True
		return False

	def _Escape_DLS(self, depth = 0):
		if depth < self.escapedepth:
			state = self.game.Freeze()
			for i in self.input_substrings:
				self.game.Thaw(state)
				for j in i:  self.game.Input(j)
				if self.game.Heuristic() < self.escape_heur:
					return i
				result = self._Escape_DLS(depth+1)
				if result is not None:
					return i + result
		return None
		

	def Step(self):
		# see if rerunning the last sequence will work again
		if self.new_best is not None:
			self.game.Thaw(self.current_state)
			if self._RunString(self.new_best):
				print self.new_best, 'immagonnaween'
				self.input_log += self.new_best
				yield self.game.Draw()
				return
			print self.new_best

		# otherwise, find things
		start_state = self.current_state
		self.new_best = None
		for i in self.input_substrings:
			if self.terminated:  break
			self.game.Thaw(start_state)
			self._RunString(i)
			yield self.game.Draw()

		# see if we're stuck in a local min
		if self.new_best is None and not self.terminated:
			print 'Wario: temporarily stuck, depth-limited search to escape...'
			self.escape_heur = self.current_heur
			result = self._Escape_DLS()
			if result is None:
				print 'Wario: stuck in a local minimum or unable to see any progress.'
				self.terminated = True
				self.new_best = []
			else:
				print 'Wario: found an escape.'
				self.game.Thaw(start_state)
				self._RunString(result)

		self.input_log += self.new_best

	def Event(self, evt):
		if evt.type == pygame.QUIT:  self.terminated = True

	def Victory(self):
		return self.game.Victory() or self.terminated

	def Path(self):
		return self.input_log

LoadedBrain = Wario
