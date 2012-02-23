#!/usr/bin/env python2

"""
An Optiness "pathfinder" that plays back recorded input
Darren Alton
"""

import pygame, cPickle
import os, wave
from array import array

from skeleton_solver import Brain

defaultargs = { 'fps':         60, # run at 60fps because we have a human watching
				'file':        'output/last_run.pickle',
				'granularity': 1,  # mostly for converting SuperOpti runs to 60fps
				'force':       False,
				'recordvideo': False,
				'recordaudio': False }

validargs = { 'fps':         lambda x: x >= 0,
			  'file':        os.path.isfile,
			  'granularity': lambda x: x > 0 }

class Rerun(Brain):
	name = 'rerun'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.clock = pygame.time.Clock()
		self.fps = self.args['fps']
		self.force = self.args['force']
		self.granularity = self.args['granularity']
		self.recordvideo = self.args['recordvideo']
		self.recordaudio = self.args['recordaudio']

		loadedfile = cPickle.load(open(self.args['file'], 'r'))

		if self.recordaudio:
			# todo: some way to determine appropriate framerate from game.  currently using values for snes
			self.wav = wave.open('output/{}_{}.wav'.format(self.__class__.name, self.game.__class__.name), 'wb')
			self.wav.setnchannels(2)
			self.wav.setsampwidth(2)
			self.wav.setframerate(32040)

		# describe the run
		print 'replaying a run of:\t', loadedfile['game'], '\t', loadedfile['game_args']
		print 'that was produced by:\t', loadedfile['brain'], '\t', loadedfile['brain_args']
		if not self.force:
			if loadedfile['game'] != game.__class__.name:
				raise Exception('loaded input string is for "%s"' % (loadedfile['game']))

			special_cases = ['granularity', 'audio']
			mismatches = []
			for key in game.args:
				if key not in special_cases:
					# note: old args being dropped are implicitly ignored by this loop.
					# explicitly ignore new features with this conditional.
					if key in loadedfile['game_args'] and loadedfile['game_args'][key] != game.args[key]:
						mismatches.append(key)
				else:
					if key == 'granularity':
						then = loadedfile['game_args'][key]
						if key in loadedfile['brain_args']:
							then *= loadedfile['brain_args'][key]
						now = game.args[key]*self.args[key]
						if then != now:
							print 'rerun: granularity mismatch! consider adjusting rerun\'s granularity.'
							mismatches.append(key)
					elif key == 'audio':
						print 'rerun: be sure to use "array" for the game audio if you want to use rerun\'s sound recording.'
			if len(mismatches) > 0:
				for key in mismatches:
					print key, '\n\tgame:', game.args[key],
					print '\n\tfile:', loadedfile['game_args'][key]
				raise Exception('game_args mismatch')

		self.inputstring = loadedfile['path']
		self.outputstring = []
		print 'with', len(self.inputstring), 'frames of input'

	def Step(self):
		if self.fps > 0:  self.clock.tick(self.fps)
		frameinput = 0

		if len(self.inputstring):  frameinput = self.inputstring.pop(0)

		for i in xrange(self.granularity):
			self.game.Input(frameinput)
			self.outputstring.append(frameinput)
			surf = self.game.Draw()

			if self.recordvideo:
				pygame.image.save( surf,
								   'output/%s_%s_%04d.png' % ( self.__class__.name,
				                                               self.game.__class__.name,
				                                               len(self.outputstring) ) )
			if self.recordaudio:
				self.wav.writeframesraw(array('H', self.game.Sound()).tostring())
				if self.Victory() and i == self.granularity-1:
					self.wav.close()

			yield surf


	def Path(self):
		return self.outputstring

	def Victory(self):
		return len(self.inputstring) <= 0

LoadedBrain = Rerun
