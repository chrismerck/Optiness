#!/usr/bin/env python2

"""
An Optiness "pathfinder" that plays back recorded input
Darren Alton
"""

import pygame, cPickle
import wave
from array import array

from skeleton_solver import Brain

defaultargs = { 'fps': 60, # run at 60fps because we have a human watching
				'file': 'inputstring.pickle',
				'granularity': 1, # mostly for converting SuperOpti runs to 60fps
				'force': False,
				'record': False,
				'wavfile': None }

class Rerun(Brain):
	name = 'rerun'

	def __init__(self, game, args = {}):
		Brain.__init__(self, game, args, defaultargs)

		self.clock = pygame.time.Clock()
		self.fps = self.args['fps']
		self.force = self.args['force']
		self.granularity = self.args['granularity']
		self.record = self.args['record']
		self.wavfile = self.args['wavfile']
		self.wavlog = []

		loadedfile = cPickle.load(open(self.args['file'], 'r'))

		# describe the run
		print 'replaying a run of:\t', loadedfile['game'], '\t', loadedfile['game_args']
		print 'that was produced by:\t', loadedfile['brain'], '\t', loadedfile['brain_args']
		if not self.force:
			if loadedfile['game'] != game.__class__.name:
				raise Exception('loaded input string is for "%s"' % (loadedfile['game']))
			if loadedfile['game_args'] != game.args:
				raise Exception('game_args mismatch:\n%s\n%s' % (loadedfile['game_args'], game.args))

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
			if self.record:
				pygame.image.save( surf,
								   '%s_%s_%04d.png' % ( self.__class__.name,
														self.game.__class__.name,
														len(self.outputstring) ) )
			if self.wavfile is not None:
				self.wavlog += self.game.Sound()
				if self.Victory():
					wav = wave.open(self.wavfile, 'wb')
					wav.setnchannels(2)
					wav.setsampwidth(2)
					wav.setframerate(32000)
					wav.writeframes(array('H', self.wavlog).tostring())
					wav.close()
					self.wavfile = None

			yield surf

	def Path(self):
		return self.outputstring

	def Victory(self):
		return len(self.inputstring) <= 0

LoadedBrain = Rerun
