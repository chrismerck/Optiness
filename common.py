#!/usr/bin/env python2

"""
Driver class to run a pathfinder on a gamecore

Darren Alton
"""

import pygame   # this level was removed from Donkey Kong for its NES release
import cPickle  # a sea cucumber left in brine
import os       # generic brand cheerios
import sys      # a nickname that refers to a female sybling
import time     # an illusion

game_path = './games'
brain_path = './brains'

blacklist = ['skeleton_game', 'skeleton_solver']

sys.path.append(game_path)
sys.path.append(brain_path)

class UtilType:
	def ListModules(self, path):
		files = os.listdir(path)
		for i in files:
			if '.' in i:
				name,ext = i.rsplit('.', 1)
				if ext == 'py' and name not in blacklist:
					yield name

	def ListGames(self):  return self.ListModules(game_path)
	def ListBrains(self): return self.ListModules(brain_path)

	def GetArgs(self, modname):
		return __import__(modname).defaultargs.copy()

util = UtilType()


class Driver:
	def __init__(self, game_mod_name, brain_mod_name, game_args={}, brain_args={}, scale=1):
		self.game = __import__(game_mod_name).LoadedGame(game_args)
		self.brain = __import__(brain_mod_name).LoadedBrain(self.game, brain_args)

		self.scale = scale

		xmax, ymax = self.brain.ScreenSize()
		self.winsize = (xmax*scale, ymax*scale)
		self.screen = pygame.display.set_mode(self.winsize)

	def Run(self):
		running = True
		print 'Driver: Started at', time.asctime()
		while running:
			# let the pathfinder take a step, get screens to show throughout
			for surf in self.brain.Step():
				# process events
				for event in pygame.event.get():
					# pass events on to the pathfinder in case it takes input etc.
					self.brain.Event(event)
					if event.type == pygame.QUIT:
						running = False
				# if relevant, draw the screen
				if surf is not None:
					# scale it, and show it
					scaled = surf
					if self.scale != 1:
						scaled = pygame.transform.scale(surf, self.winsize)
					self.screen.blit(scaled, (0,0))
				pygame.display.flip()
			pygame.display.flip()

			if self.brain.Victory():
				running = False
		print 'Driver: Finished at', time.asctime()

	def Save(self, output, screenshot=None):
		result = {
			'game':       self.game.__class__.name,
			'game_args':  self.game.args,
			'brain':      self.brain.__class__.name,
			'brain_args': self.brain.args,
			'path':       self.brain.Path(),
			'state':      self.game.Freeze()
		}
		cPickle.dump( result, open(output, 'w') )

		if screenshot is not None:
			pygame.image.save(self.screen, screenshot)
