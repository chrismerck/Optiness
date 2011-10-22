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
	def __init__(self, state, fscores):
		self.state = state
		self.f = fscores
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
		f_score = {}

		# singleton-set containing the initial state.  must use StateWrappers.
		openset = [ StateWrapper(self.game.Freeze(), f_score) ]

		# we should index these with states rather than wrappers
		# ... and even that isn't sustainable, so we'll have to
		#     come up with something better later
		closedset = set()
		came_from = {}
		g_score = { start: 0 }
		h_score = { start: self.game.Heuristic() }

		f_score[start] = g_score[start] + h_score[start]

		while len(openset) > 0: # while not empty
			x = heappop(openset).state # get the lowest f=g+h of the openset
			self.game.Thaw(x)
			if self.game.Victory():
				self.input_log = self._ReconstructPath(came_from, x)
				return

			closedset.add(x)
			for inp in self.game.ValidInputs():
				self.game.Thaw(x)
				self.game.Input(inp)
				y = self.game.Freeze()

				if y in closedset: continue
				yield self.game.Draw() # only show if we've not seen this state yet

				tentative_g = g_score[x] + 1
				yw = StateWrapper(y, f_score)
				if yw not in openset:
					heappush(openset, yw)
					tentative_better = True
				elif tentative_g < g_score[y]:
					tentative_better = True
				else:
					tentative_better = False

				if tentative_better:
					came_from[y] = (x, inp)
					g_score[y] = tentative_g
					h_score[y] = self.game.Heuristic()
					f_score[y] = g_score[y] + h_score[y]
					print f_score[y], '=', g_score[y], '+', h_score[y]


	def Path(self):
		return self.input_log

LoadedBrain = Sagan
