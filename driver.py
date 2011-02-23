#!/usr/bin/env python2

"""
Rudimentary driver program to run an Optiness pathfinder on a gamecore
Darren Alton

"""

# this level was removed from Donkey Kong for its NES release
import pygame

# a nyckname that refers to a female sybling
import sys

# Optiness engine modules
sys.path.append('./gamecores')
import maze

# Optiness solver modules
sys.path.append('./pathfinders')
import dawkins

# the hell did you just call me, PUNK?
if __name__ == "__main__":
	# we want to make the output of Maze bigger
	scale = 4
	pxmax = maze.xmax*scale
	pymax = maze.ymax*scale

	screen = pygame.display.set_mode((pxmax,pymax))

	testmaze = maze.Maze(1)
	pop = dawkins.Population(30, testmaze)

	running = True
	while running:
		# process events (just "quit" for now)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		# we deviate a bit from the biblical record here
		pop.Evolve()

		# get the screen from the game engine, scale it, and show it
		surf = testmaze.Draw()
		scaled = pygame.transform.scale(surf, (pxmax,pymax))
		screen.blit(scaled, scaled.get_rect())
		pygame.display.flip()

