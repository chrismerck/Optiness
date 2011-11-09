#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses a greedy algorithm with low memory costs
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'lookahead':      3,
				'walkahead':      2,
				'escapedepth':    4,
				'shortcutrepeat': False }

class Wario(Brain):
	name = 'wario'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.lookahead = self.args['lookahead']
		self.walkahead = self.args['walkahead']
		self.escapedepth = self.args['escapedepth']
		self.shortcutrepeat = self.args['shortcutrepeat']

		self.input_log = []
		self.new_best = None
		self.terminated = False

		self._GenInputLists(self.lookahead)

		self.current_state = self.game.Freeze()
		self.current_heur = self.game.Heuristic()
		self.escape_heur = self.current_heur

		self.screen = pygame.Surface(self.ScreenSize())
		self.screenmidpoint = self.screen.get_width() / 2


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
		pygame.display.set_caption('{} vs. {}'.format(self.current_heur, h))
		if h < self.current_heur:
			self.new_best = instring
			self.current_heur = h
			self.current_state = self.game.Freeze()
			self._UpdateScreen(right=False)
			return True
		return False

	def _Escape_DLS(self, depth = 0):
		if depth < self.escapedepth:
			state = self.game.Freeze()
			for i in self.input_substrings:
				self.game.Thaw(state)
				for j in i:  self.game.Input(j)
				h = self.game.Heuristic()
				self.driverscreen.blit(self._UpdateScreen(), (0,0))
				pygame.display.flip()
				pygame.display.set_caption('{} vs. {} (escape)'.format(self.escape_heur, h))
				if h < self.escape_heur:
					return i
				result = self._Escape_DLS(depth+1)
				if result is not None:
					return i + result
		return None

	def _UpdateScreen(self, right=True):
		x = 0
		if right: x = self.screenmidpoint
		self.screen.blit(self.game.Draw(), (x,0))
		return self.screen

	def Step(self):
		# see if rerunning the last sequence will work again
		if self.shortcutrepeat and self.new_best is not None:
			self.game.Thaw(self.current_state)
			if self._RunString(self.new_best):
				# TODO: some sort of hack to backpedal an 'appropriate' amount?
				self.input_log += self.new_best
				yield self._UpdateScreen()
				return

		# otherwise, find things
		start_state = self.current_state
		self.new_best = None
		for i in self.input_substrings:
			if self.terminated:  return
			self.game.Thaw(start_state)
			self._RunString(i)
			yield self._UpdateScreen()

		# see if we're stuck in a local min
		if self.new_best is None:
			print 'Wario: temporarily stuck, depth-limited search to escape...'
			self.escape_heur = self.current_heur
			self.driverscreen = pygame.display.get_surface()
			result = self._Escape_DLS()
			if result is None:
				print 'Wario: stuck in a local minimum or unable to see any progress.'
				self.terminated = True
				self.new_best = []
			else:
				print 'Wario: found an escape.'
				self.game.Thaw(start_state)
				for j in result:  self.game.Input(j)
				self.new_best = result
				self.current_heur = self.game.Heuristic()
				self.current_state = self.game.Freeze()
				self.input_log += result
				yield self._UpdateScreen(right=False)
				return

		# only take 'walkahead' steps just in case we run into the DANGER ZONE
		self.game.Thaw(start_state)
		tmp = self.new_best[:self.walkahead]
		for j in tmp:  self.game.Input(j)
		self.current_state = self.game.Freeze()
		self.input_log += tmp

	def Event(self, evt):
		if evt.type == pygame.QUIT:  self.terminated = True

	def Victory(self):
		return self.game.Victory() or self.terminated

	def Path(self):
		return self.input_log

	# double width because we show 'current best' and 'current attempt' side by side
	def ScreenSize(self):
		w,h = self.game.ScreenSize()
		return (w*2,h)

LoadedBrain = Wario
