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
	def __le__(self, other):
		return self.f[self.state] <= other.f[self.state]

class Sagan(Brain):
	name = 'sagan'

	def __init__(self, game):
		self.supported_games = [ 'maze', 'snes' ]
		Brain.__init__(self, game)
		self.input_log = None


	def _ReconstructPath(self, came_from, state):
		if state not in came_from:
			return []
		# "else"
		curr = came_from[state]
		p = self._ReconstructPath(came_from, curr[0])
		p.append(curr[1])
		return p

	def Step(self):
		f_score = {}
		start = StateWrapper(self.game.Freeze(), f_score)

		openset = [ start ] # singleton-set containing the initial state

		# we should index these with states rather than wrappers
		# ... and even that isn't sustainable, so we'll have to
		#     come up with something better later
		closedset = set()
		came_from = {}
		g_score = { start.state: 0 }
		h_score = { start.state: self.game.Heuristic() }

		f_score[start.state] = g_score[start.state] + h_score[start.state]

		while len(openset) > 0: # while not empty
			x = heappop(openset) # get the lowest f=g+h of the openset
			self.game.Thaw(x.state)
			if self.game.Victory():
				self.input_log = self._ReconstructPath(came_from, x.state) # TODO
				return

			closedset.add(x.state)
			for inp in self.game.ValidInputs():
				self.game.Thaw(x.state)
				self.game.Input(inp)
				y = StateWrapper(self.game.Freeze(), f_score)

				if y.state in closedset: continue
				yield self.game.Draw() # only show if we've not seen this state yet

				tentative_g = g_score[x.state] + 1
				tentative_better = True
				if y not in openset:
					heappush(openset, y)
				elif tentative_g >= g_score[y.state]:
					tentative_better = False

				if tentative_better:
					came_from[y.state] = (x.state, inp)
					g_score[y.state] = tentative_g
					h_score[y.state] = self.game.Heuristic()
					f_score[y.state] = g_score[y.state] + h_score[y.state]
					print f_score[y.state], g_score[y.state], h_score[y.state]


	def Path(self):
		return self.input_log

LoadedBrain = Sagan
