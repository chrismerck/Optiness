#!/usr/bin/env python2
"""
A SuperOpti heuristic for SNES Super Mario World

By Darren Alton
"""

def Heuristic(self):
	dead = float('inf')
	level_end = 4830
	level_ground_ypos = 380
	mario_dead_anim = 9

	mario_x = self._Word(0xD2,0xD1)
	mario_y = self._Word(0xD4,0xD3)
	mario_anim = self._Byte(0x71)

	if mario_anim == mario_dead_anim or mario_y > level_ground_ypos:
		return dead

	return level_end - mario_x
