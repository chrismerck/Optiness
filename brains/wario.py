#!/usr/bin/env python2

"""
An Optiness "pathfinder" that uses a greedy algorithm with low memory costs
Darren Alton
"""

import pygame
from bisect import insort

from skeleton_solver import Brain

defaultargs = { 'step':          1,
				'peek':          1,
				'method':        'dfs',
				'escapedepth':   4,
				'escapemethod':  'dfs',
				'repeathistory': 0,
				'motionblur':    False }

validargs = { 'step':          lambda x: x > 0,
			  'peek':          lambda x: x >= 0,
			  'method':        ['dfs', 'bfs'],
			  'escapedepth':   lambda x: x >= 0,
			  'escapemethod':  ['dfs', 'bfs'],
			  'repeathistory': lambda x: x >= 0 }

class Wario(Brain):
	name = 'wario'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.step = self.args['step']
		self.peek = self.args['peek']
		self.method = self.args['method']
		self.escapedepth = self.args['escapedepth']
		self.escapemethod = self.args['escapemethod']
		self.repeathistory = self.args['repeathistory']
		self.motionblur = self.args['motionblur']
		self.input_log = []
		self.history = []
		self.deuxiemevue_buffer = []

		self.best_state = self.game.Freeze()
		self.best_heur = self.game.Heuristic()

		self.screen = pygame.Surface(self.ScreenSize())
		self.screenmidpoint = self.screen.get_width() / 2

		self._AddChildren = self._AddChildrenDFS
		if self.method == 'bfs':  self._AddChildren = self._AddChildrenBFS

		self._AddChildrenEscape = self._AddChildrenDFS
		if self.escapemethod == 'bfs':  self._AddChildrenEscape = self._AddChildrenBFS
		

	def _UpdateScreen(self, surf=None, right=True):
		if surf is None:  surf = self.game.Draw()

		x = 0
		if right: x = self.screenmidpoint

		if surf is not None:
			self.screen.blit(surf, (x,0))

		return self.screen

	def _CheckAndUpdateBest(self, img=None, historical=False):
		# find out if the node we're exploring is promising
		current = self.game.Freeze()
		h = self._LookAhead(current)
		hh = h

		if historical:
			hh = float('inf')
			for hist_entry in self.history:
				self._RunString(hist_entry[1], current)
				hh = min(hh, self._LookAhead())

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

	# do a longer depth-limited search looking for anything better at all
	def _Escape(self):
		maxdepth = self.escapedepth
		if maxdepth <= 0:  return None

		start_state = self.best_state
		fringe = [(0,[])]
		while len(fringe) and not self.terminated:
			depth,instring = self._GrabAndRun(fringe, start_state)

			# dying is the coward's way out
			if self.game.Defeat():
				continue

			# if we have a win, use it
			if self.game.Victory():
				return instring

			# only bother with depths we haven't tried already
			if depth > self.step:
				# if we found a lower heuristic, we can escape
				if self._CheckAndUpdateBest():
					return instring

			# use either DFS or BFS, as configured in __init__
			self._AddChildrenEscape(fringe, instring, depth, maxdepth)

		self.game.Thaw(start_state)
		return None

	def _RepeatHistory(self):
		# only if the history has a bit of a repertoire should we use it
		if len(self.history) == self.repeathistory:
			start_state = self.best_state
			start_heur = self.best_heur
			best_instring = []

			for i in xrange(len(self.history)):
				# reusing _GrabAndRun is a bit of a hack here.  see if you can figure out why!
				dh_old,instring,img = self._GrabAndRun([self.history[i]], start_state, render=True)

				# if it's a new best, update things to reflect that
				if self._CheckAndUpdateBest(img, historical=True):
					best_instring = instring
					# update its historical score if necessary
					dh_new = self.best_heur - start_heur
					if dh_new < dh_old:
						self.history[i] = (dh_new, instring)
						self.history.sort()

				yield self._UpdateScreen(surf=img)

			# if repeating history worked, use it.
			# TODO: threshold it more aggressively than "<"
			if self.best_heur < start_heur:
				self.input_log += best_instring
				self.repeated = True

	# update the history (sorted by delta heur)
	def _UpdateHistory(self, dh, best_instring):
		hist_entry = (dh, best_instring)
		# if it's not the first input string we have...
		if dh != float('-inf'):
			# if it's not full and the string isn't already in there...
			if len(self.history) < self.repeathistory:
				found = False
				for dh,instring in self.history:
					if instring == best_instring:
						found = True
						break
				if not found:
					insort(self.history, hist_entry)
			# if it is full (and we have a history at all)...
			elif len(self.history):
				# if it's better than our worst, replace our worst
				if hist_entry < self.history[-1]:
					self.history[-1] = hist_entry
					self.history.sort()

	# do a depth-limited search looking for the best input string to use
	def Step(self):
		maxdepth = self.step
		start_state = self.best_state
		start_heur = self.best_heur
		best_instring = []

		# try repeating history
		self.repeated = False
		for i in self._RepeatHistory():  yield i
		if self.repeated:  return

		# otherwise, search properly
		fringe = [(0,[])]
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
			dh = (self.best_heur - start_heur)
			self._UpdateHistory(dh, best_instring)
		elif not self.terminated:
			print 'Wario: got stuck, attempting a deeper search to escape...',
			escape_path = self._Escape()
			if escape_path is not None:
				print 'found an escape!'
				self.input_log += escape_path
			else:
				print 'could not escape local minimum.'
				self.terminated = True

	def Path(self):
		return self.input_log

	# double width because we show 'current best' and 'current attempt' side by side
	def ScreenSize(self):
		w,h = self.game.ScreenSize()
		return (w*2,h)

LoadedBrain = Wario
