#!/usr/bin/env python2

"""
Rudimentary driver program to run an Optiness pathfinder on a gamecore
Darren Alton
"""

# this level was removed from Donkey Kong for its NES release
import pygame

# a nyckname that refers to a female sybling
import sys

# Optiness engine and solver modules
sys.path.append('./gamecores')
sys.path.append('./pathfinders')


def main():
	engine_name, solver_name = ('maze', 'dawkins')

	if len(sys.argv) == 3:
		engine_name = sys.argv[1]
		solver_name = sys.argv[2]

	engine = __import__(engine_name)
	solver = __import__(solver_name)

	# we want to make the display output bigger
	scale = 4
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
			else:
				brain.Event(event)

		# let the pathfinder take a step, get the screen from the game, scale it, and show it
		surf = brain.Step()
		scaled = pygame.transform.scale(surf, (pxmax,pymax))
		screen.blit(scaled, scaled.get_rect())
		pygame.display.flip()


if __name__ == "__main__":  main()
