#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses A-Star
Darren Alton
"""

import pygame

from skeleton_solver import Brain
from heapq import *

# for the purposes of minheaping our savestates...
class StateWrapper:
	def __init__(self, state, f):
		self.state = state
		self.f = f
	def __eq__(self, other):
		return self.state == other.state
	def __le__(self, other):
		return self.f[self.state] <= other.f[self.state]

class Sagan(Brain):
	name = 'sagan'

	def __init__(self, game):
		self.supported_games = [ 'maze', 'snes' ]
		Brain.__init__(self, game)
		self.input_log = None

	def Victory(self):
		return self.input_log is not None

	def _ReconstructPath(self, came_from, state):
		if state not in came_from:
			return []
		# "else"
		curr = came_from[state]
		p = self._ReconstructPath(came_from, curr[0])
		p.append(curr[1])
		return p

	def Step(self):
		start = self.game.Freeze()

		g = { start: 0 }
		h = { start: self.game.Heuristic() }
		f = { start: g[start] + h[start] }

		# singleton-set minheap containing the initial state.
		# must use StateWrapper so the minheap-related functions work.
		openset = [ StateWrapper(start, f) ]

		# we should index these with states rather than wrappers
		# ... and even that isn't sustainable, so we'll have to
		#     come up with something better later
		closedset = set()
		came_from = {}

		while len(openset) > 0: # while not empty
			x = heappop(openset).state # get the lowest f=g+h of the openset
			self.game.Thaw(x)
			if self.game.Victory():
				self.input_log = self._ReconstructPath(came_from, x)
				yield self.game.Draw()
				return

			closedset.add(x)
			for inp in self.game.ValidInputs():
				self.game.Thaw(x)
				self.game.Input(inp)
				y = self.game.Freeze()

				if y in closedset: continue
				yield self.game.Draw() # only show if we've not seen this state yet

				tentative_g = g[x] + 1
				y_wrapped = StateWrapper(y, f)
				tentative_better = True
				if y_wrapped not in openset:
					heappush(openset, y_wrapped)
				elif tentative_g >= g[y]:
					tentative_better = False

				if tentative_better:
					came_from[y] = (x, inp)
					g[y] = tentative_g
					h[y] = self.game.Heuristic()
					f[y] = g[y] + h[y]


	def Path(self):
		return self.input_log

LoadedBrain = Sagan
