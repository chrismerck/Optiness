#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses A-Star
Darren Alton
"""

import pygame

from skeleton_solver import Brain
from heapq import *

defaultargs = {}

class SaganNode:
	def __init__(self, game, parent=None, input=None):
		self.state = game.Freeze()
		self.g = 0
		self.h = game.Heuristic()
		self.victory = game.Victory()
		if parent is not None:  parent.Adopt(self, input)
		else:  self.parent = None

	def Adopt(self, child, input):
		child.parent = self
		child.input = input
		child.g = self.g + 1

	def GetState(self):
		# this is a function so we can deal with making a disk cache
		return self.state

	def ReconstructPath(self):
		if self.parent is None:  return []
		# "else"
		p = self.parent.ReconstructPath()
		p.append(self.input)
		return p

	def f(self):
		return self.g + self.h

	def Victory(self):
		return self.victory

	def __le__(self, other):  return self.f() <= other.f()
	def __eq__(self, other):  return self.GetState() == other.GetState()
	def __hash__(self):       return hash(self.GetState())

class Sagan(Brain):
	name = 'sagan'
	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)
		self.input_log = None

	def Step(self):
		# singleton-set minheap containing the initial state.
		openset = [ SaganNode(self.game) ]
		closedset = set()

		# while lowest rank in OPEN is not the GOAL
		while not openset[0].Victory():
			# get the best (lowest f=g+h) of the fringe
			x = heappop(openset)
			closedset.add(x)
			for inp in self.game.ValidInputs():
				self.game.Thaw(x.GetState())
				self.game.Input(inp)
				y = SaganNode(self.game, x, inp)

				if y in closedset:  continue
				yield self.game.Draw() # only show if we've not seen this state yet

				tentative_better = True
				if y not in openset:  heappush(openset, y)
				elif x.g+1 >= y.g:  tentative_better = False

				if tentative_better:  x.Adopt(y, inp)

		self.input_log = openset[0].ReconstructPath()
		yield self.game.Draw()
		print 'Sagan: end of A* search.'

	def Victory(self):
		return self.input_log is not None

	def Path(self):
		return self.input_log
	

LoadedBrain = Sagan
