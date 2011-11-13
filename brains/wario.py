#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses a greedy algorithm with low memory costs
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'lookahead': 3,
				'walkahead': 2 }

class Wario(Brain):
	name = 'wario'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.lookahead = self.args['lookahead']
		self.walkahead = self.args['walkahead']

		self.input_log = []
		self.terminated = False

		self.best_state = self.game.Freeze()
		self.best_heur = self.game.Heuristic()

		self.screen = pygame.Surface(self.ScreenSize())
		self.screenmidpoint = self.screen.get_width() / 2

	def _UpdateScreen(self, surf=None, right=True):
		if surf is None:  surf = self.game.Draw()

		x = 0
		if right: x = self.screenmidpoint

		self.screen.blit(surf, (x,0))
		return self.screen

	def _RunString(self, instring, state=None):
		if state is not None:  self.game.Thaw(state)
		for j in instring:
			self.game.Input(j)

	def _LookAhead(self, start_state, maxdepth):
		min_heur = self.game.Heuristic()
		if maxdepth <= 0:  return min_heur

		fringe = [(0,[])]
		while len(fringe) and not self.terminated:
			depth,instring = fringe.pop()
			self._RunString(instring, start_state)

			# if dead, it's unlikely any children will be improved
			if self.game.Defeat():
				continue

			# if we found a new best heuristic, update it
			min_heur = min( min_heur, self.game.Heuristic() )

			# add new children to explore if we haven't hit our limit
			if depth < maxdepth:
				for child in self.game.ValidInputs():
					fringe.append( ( depth+1, instring+[child] ) )

		self.game.Thaw(start_state)
		return min_heur

	def Step(self):
		start_state = self.best_state
		best_instring = []
		maxdepth = self.walkahead
		peek = self.lookahead - self.walkahead

		fringe = [(0,[])]
		while len(fringe) and not self.terminated:
			depth,instring = fringe.pop()
			self._RunString(instring, start_state)
			img = self.game.Draw()

			# prune, don't bother exploring nodes at or past a death
			if depth > 0 and self.game.Defeat():
				continue

			# find out if the node we're exploring is promising
			current = self.game.Freeze()
			h = self._LookAhead(current, peek)

			# give some insight to the user
			s = '{} vs. {}'.format(self.best_heur, h)
			pygame.display.set_caption(s)
			yield self._UpdateScreen(surf=img)

			# if it's a new best, update things to reflect that
			if h < self.best_heur:
				self.best_heur = h
				self.best_state = current
				best_instring = instring
				self._UpdateScreen(surf=img, right=False)

			# add new children to explore if we haven't hit our limit
			if depth < maxdepth:
				for child in self.game.ValidInputs():
					fringe.append( ( depth+1, instring+[child] ) )

		if len(best_instring):
			self.input_log += best_instring
		elif not self.terminated:
			print 'got stuck.'
			self.terminated = True

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
