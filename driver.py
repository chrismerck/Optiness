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


def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hg:b:", ["help", "game=", "brain="])
	except getopt.GetoptError, err:
		print str(err)
		#usage()
		sys.exit(2)

	game_mod_name, brain_mod_name = ('maze', 'sagan')
	game_args, brain_args = ({}, {})
	for o,a in opts:
		if o in ('-h', '--help'):
			usage()
		elif o in ('-g', '--game'):
			subargs = a.split(',')
			game_mod_name = subargs[0]
			for i in subargs[1:]:
				key,val = i.split(':')
				game_args[key] = val
		elif o in ('-b', '--brain'):
			subargs = a.split(',')
			brain_mod_name = subargs[0]
			for i in subargs[1:]:
				key,val = i.split(':')
				brain_args[key] = val

	game_mod = __import__(game_mod_name)
	brain_mod = __import__(brain_mod_name)

	# we may want to make the display output bigger
	scale = game_mod.scale
	pxmax = game_mod.xmax*scale
	pymax = game_mod.ymax*scale

	screen = pygame.display.set_mode((pxmax,pymax))

	game = game_mod.LoadedGame(game_args)
	brain = brain_mod.LoadedBrain(game) #, brain_args

	running = True
	while running:
		# let the pathfinder take a step, get screens to show throughout
		for surf in brain.Step():
			# process events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				else: # pass other events on to the pathfinder in case it takes input
					brain.Event(event)
			# if relevant, draw the screen
			if surf is not None:
				# scale it, and show it
				scaled = surf
				if scale != 1: scaled = pygame.transform.scale(surf, (pxmax,pymax))
				screen.blit(scaled, scaled.get_rect())
			pygame.display.flip()
		pygame.display.flip()

		if brain.Victory(): running = False

	result = {
		'game': game_mod.LoadedGame.name,
		'brain': brain_mod.LoadedBrain.name,
		'path': brain.Path(),
		'state': game.Freeze()
	}
	cPickle.dump( result, open('inputstring.pickle', 'w') )
	pygame.image.save(screen, 'endgame.png')

if __name__ == "__main__":  main()
