#!/usr/bin/env python2
"""
A SuperOpti heuristic for NES Pac-Man

By Darren Alton
"""

def Heuristic(self):
	pacman_dead_anim = 18

	pacman_anim = self._Byte(0x32)
	dots_remaining = self._Byte(0x6A)

	# if dead, return a lousy score
	if pacman_anim >= pacman_dead_anim:  return 255

	return dots_remaining
