#!/usr/bin/env python2

"""
Like Wario, but doesn't demand a better score at every step, just takes the best available.
Darren Alton
"""

import pygame

from skeleton_solver import Brain

defaultargs = { 'step': 1,
				'peek': 1,
				'method': 'dfs',
				'motionblur': False }

class Waluigi(Brain):
	name = 'waluigi'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.step = self.args['step']
		self.peek = self.args['peek']
		self.method = self.args['method']
		self.motionblur = self.args['motionblur']

		self.input_log = []

		self.best_state = self.game.Freeze()
		self.best_heur = self.game.Heuristic()

		self.screen = pygame.Surface(self.ScreenSize())
		self.screenmidpoint = self.screen.get_width() / 2

		self._AddChildren = self._AddChildrenDFS
		if self.method == 'bfs':  self._AddChildren = self._AddChildrenBFS



	def _UpdateScreen(self, surf=None, right=True):
		if surf is None:  surf = self.game.Draw()

		x = 0
		if right: x = self.screenmidpoint

		if surf is not None:
			self.screen.blit(surf, (x,0))

		return self.screen

	def _CheckAndUpdateBest(self, img=None):
		# find out if the node we're exploring is promising
		current = self.game.Freeze()
		h = self._LookAhead(current)
		hh = h

		# give some insight to the user
		s = '{} vs. {}'.format(self.best_heur, h)
		pygame.display.set_caption(s)

		# if it's a new best, update things to reflect that
		if hh < self.best_heur:
			self.best_heur = h
			self.best_state = current
			if img is not None:
				self._UpdateScreen(surf=img, right=False)
			return True

		return False

	def _RunString(self, instring, state=None):
		if state is not None:
			self.game.Thaw(state)

		for j in instring:
			self.game.Input(j)

	def _GrabAndRun(self, fringe, state, render=False):
		depth,instring = fringe.pop()

		if state is not None:
			self.game.Thaw(state)

		if render and self.motionblur:
			surf = self.game.Draw()
			for j in instring:
				self.game.Input(j)
				stepsurf = self.game.Draw()
				if surf is None:
					surf = stepsurf
				else:
					stepsurf.set_alpha(160)
					surf.blit(stepsurf, (0,0))
			return (depth,instring,surf)

		self._RunString(instring)
		if render:
			return ( depth, instring, self.game.Draw() )

		return (depth,instring)

	# add new children to explore if we haven't hit our limit
	def _AddChildrenDFS(self, fringe, instring, depth, maxdepth):
		if depth < maxdepth:
			for child in self.game.ValidInputs():
				fringe.append( ( depth+1, instring+[child] ) )

	# same as above, but makes the search breadth-first rather than depth-first
	def _AddChildrenBFS(self, fringe, instring, depth, maxdepth):
		if depth < maxdepth:
			for child in self.game.ValidInputs():
				fringe.insert( 0, ( depth+1, instring+[child] ) )

	# return the score of the best possible future of a given state
	def _LookAhead(self, start_state=None):
		min_heur = self.game.Heuristic()
		maxdepth = self.peek
		if maxdepth <= 0:
			pygame.event.pump()
			return min_heur

		if start_state is None:
			start_state = self.game.Freeze()

		fringe = [(0,[])]
		while len(fringe) and not self.terminated:
			depth,instring = self._GrabAndRun(fringe, start_state)

			# if dead, it's unlikely any children will be improved
			if self.game.Defeat():
				continue

			# allow the program to be quit, and respond to OS things while busy
			if pygame.event.peek(pygame.QUIT):
				self.terminated = True
			else:
				pygame.event.pump()

			# if we found a new best heuristic, update it
			min_heur = min( min_heur, self.game.Heuristic() )

			# only use DFS for this, not configurable...  shouldn't have to be (yet?)
			self._AddChildrenDFS(fringe, instring, depth, maxdepth)

		self.game.Thaw(start_state)
		return min_heur

	# do a depth-limited search looking for the best input string to use
	def Step(self):
		maxdepth = self.step
		start_state = self.best_state
		best_instring = []

		# otherwise, search properly
		fringe = [(0,[])]
		self.best_heur = float('inf')
		while len(fringe) and not self.terminated:
			depth,instring,img = self._GrabAndRun(fringe, start_state, render=True)

			# prune, don't bother exploring nodes at or past a death
			if depth > 0 and self.game.Defeat():
				continue

			# if we found a winner, we're done
			if self.game.Victory():
				best_instring = instring
				break

			# if it's a new best, update things to reflect that
			if self._CheckAndUpdateBest(img):
				best_instring = instring

			yield self._UpdateScreen(surf=img)

			# use either DFS or BFS, as configured in __init__
			self._AddChildren(fringe, instring, depth, maxdepth)

		if len(best_instring):
			self.input_log += best_instring
		elif not self.terminated:
			print 'Waluigi: got stuck.'
			self.terminated = True

	def Path(self):
		return self.input_log

	# double width because we show 'current best' and 'current attempt' side by side
	def ScreenSize(self):
		w,h = self.game.ScreenSize()
		return (w*2,h)

LoadedBrain = Waluigi
