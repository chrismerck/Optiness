#!/usr/bin/env python2

"""
Rudimentary driver program to run an Optiness pathfinder on a gamecore
Darren Alton
"""

import sys      # a nyckname that refers to a female sybling
import cPickle  # a sea cucumber left in brine
import pygame   # this level was removed from Donkey Kong for its NES release

import getopt   # argument parsing

# Optiness game and path-finding "brain" modules
sys.path.append('./gamecores')
sys.path.append('./pathfinders')

def usage():
	print 'todo: help'

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hg:b:s:o:", ["help", "game=", "brain=", "scale=", "output="])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	game_mod_name, brain_mod_name = ('maze', 'sagan')
	game_args, brain_args = ({}, {})

	# we may want to make the display output bigger
	scale = 1

	# default value for the output pickle
	output = 'inputstring.pickle'

	for o,a in opts:
		if o in ('-h', '--help'):
			usage()
		elif o in ('-g', '--game'):
			subargs = a.split(';')
			game_mod_name = subargs[0]
			for i in subargs[1:]:
				key,val = i.split(':')
				game_args[key] = val
		elif o in ('-b', '--brain'):
			subargs = a.split(';')
			brain_mod_name = subargs[0]
			for i in subargs[1:]:
				key,val = i.split(':')
				brain_args[key] = val
		elif o in ('-s', '--scale'):
			scale = int(a)
		elif o in ('-o', '--output'):
			output = a

	game_mod = __import__(game_mod_name)
	game = game_mod.LoadedGame(game_args)

	brain_mod = __import__(brain_mod_name)
	brain = brain_mod.LoadedBrain(game, brain_args)

	xmax, ymax = brain.ScreenSize()
	xmax = xmax*scale
	ymax = ymax*scale

	screen = pygame.display.set_mode((xmax,ymax))

	running = True
	while running:
		# let the pathfinder take a step, get screens to show throughout
		for surf in brain.Step():
			# process events
			for event in pygame.event.get():
				# pass events on to the pathfinder in case it takes input etc.
				brain.Event(event)
				if event.type == pygame.QUIT:  running = False
			# if relevant, draw the screen
			if surf is not None:
				# scale it, and show it
				scaled = surf
				if scale != 1: scaled = pygame.transform.scale(surf, (xmax,ymax))
				screen.blit(scaled, (0,0))
			pygame.display.flip()
		pygame.display.flip()

		if brain.Victory(): running = False

	result = {
		'game': game_mod.LoadedGame.name,
		'game_args': game_args,
		'brain': brain_mod.LoadedBrain.name,
		'brain_args': brain_args,
		'path': brain.Path(),
		'state': game.Freeze()
	}
	cPickle.dump( result, open(output, 'w') )
	pygame.image.save(screen, 'endgame.png')

if __name__ == "__main__":  main()
