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

	game_mod_name, brain_mod_name = ('maze', 'sapiens')
	for o,a in opts:
		if o in ('-h', '--help'):
			usage()
		elif o in ('-g', '--game'):
			game_mod_name = a
		elif o in ('-b', '--brain'):
			brain_mod_name = a

	game_mod = __import__(game_mod_name)
	brain_mod = __import__(brain_mod_name)

	# we want to make the display output bigger
	scale = 8
	pxmax = game_mod.xmax*scale
	pymax = game_mod.ymax*scale

	screen = pygame.display.set_mode((pxmax,pymax))

	game = game_mod.LoadedGame()
	brain = brain_mod.LoadedBrain(game)

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
				scaled = pygame.transform.scale(surf, (pxmax,pymax))
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
