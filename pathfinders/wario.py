#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses a greedy algorithm with low memory costs
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'lookahead':    3,
				'maxlookahead': 7,
				'increasetime': 2 }

class Wario(Brain):
	name = 'wario'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.lookahead = self.args['lookahead']
		self.maxlookahead = self.args['maxlookahead']
		self.increasetime = self.args['increasetime']

		self.input_log = []
		self.new_best = None
		self.terminated = False

		self._GenInputLists(self.lookahead)
		self.frames_since_increase = 0

		#self.game.Input(0) # hack for emulator to kick into gear
		self.current_state = self.game.Freeze()
		self.current_heur = self.game.Heuristic()
		self.escape_heur = self.current_heur


	def _GenInputLists(self, max, path = []):
		if len(path) == 0:
			self.input_substrings = []
		if len(path) >= max:
			self.input_substrings.append(path)
		elif not self.terminated:
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

	def Step(self):
		# see if we're done trying to escape a local minimum
		if self.frames_since_increase > 0:
			self.frames_since_increase += 1
			if self.frames_since_increase > self.increasetime:
				if self.escape_heur == self.current_heur:
					print 'Wario: could not escape from local minimum.'
					self.terminated = True
					return
				print 'Wario: reverting to a lookahead of', self.lookahead
				self._GenInputLists(self.lookahead)
				self.frames_since_increase = 0
		# otherwise, see if rerunning the last sequence will work again
		elif self.new_best is not None:
			self.game.Thaw(self.current_state)
			if self._RunString(self.new_best):
				print self.new_best, 'immagonnaween'
				self.input_log += self.new_best
				yield self.game.Draw()
				return
			print self.new_best

		# finally, find things
		start_state = self.current_state
		self.new_best = None
		for i in self.input_substrings:
			if self.terminated:  break
			self.game.Thaw(start_state)
			result = self._RunString(i)
			if result and self.frames_since_increase > 0:
				print 'Wario: seemingly escaped from local minimum'
				self._GenInputLists(self.lookahead)
				self.frames_since_increase = 0
				break
			yield self.game.Draw()

		if self.new_best is None:
			if self.frames_since_increase > 0:
				print 'Wario: got stuck in a local minimum or was unable to make visible progress.'
				self.terminated = True
			elif not self.terminated:
				print 'Wario: temporarily stuck, increasing lookahead to', self.maxlookahead
				self._GenInputLists(self.maxlookahead)
				self.escape_heur = self.current_heur
				self.frames_since_increase = 1
		else:
			self.input_log += self.new_best

	def Event(self, evt):
		if evt.type == pygame.QUIT:  self.terminated = True

	def Victory(self):
		return self.game.Victory() or self.terminated

	def Path(self):
		return self.input_log

LoadedBrain = Wario
