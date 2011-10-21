#!/usr/bin/env python2

"""
Rudimentary driver program to run an Optiness pathfinder on a gamecore
Darren Alton
"""

import sys      # a nyckname that refers to a female sybling
import cPickle  # a sea cucumber left in brine
import pygame   # this level was removed from Donkey Kong for its NES release

import getopt   # argument parsing

# Optiness engine and solver modules
sys.path.append('./gamecores')
sys.path.append('./pathfinders')


def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "he:s:", ["help", "engine=", "solver="])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	engine_name, solver_name = ('maze', 'sapiens')
	for o,a in opts:
		if o in ('-h', '--help'):
			usage()
		elif o in ('-e', '--engine'):
			engine_name = a
		elif o in ('-s', '--solver'):
			solver_name = a

	engine = __import__(engine_name)
	solver = __import__(solver_name)

	# we want to make the display output bigger
	scale = 8
	pxmax = engine.xmax*scale
	pymax = engine.ymax*scale

	screen = pygame.display.set_mode((pxmax,pymax))

	game = engine.LoadedGame()
	brain = solver.LoadedBrain(game)

	running = True
	while running:
		# process events (just "quit" for now)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			else: # pass other events on to the pathfinder in case it takes input
				brain.Event(event)

		# let the pathfinder take a step, get the screen from the game
		brain.Step()
		surf = brain.Draw()
		if surf is not None:
			# scale it, and show it
			scaled = pygame.transform.scale(surf, (pxmax,pymax))
			screen.blit(scaled, scaled.get_rect())
		pygame.display.flip()

		if brain.Victory(): running = False

	cPickle.dump( brain.Path(), open('inputstring.pickle', 'w') )

if __name__ == "__main__":  main()
