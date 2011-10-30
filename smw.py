#!/usr/bin/env python2
"""
A SuperOpti heuristic for SNES Super Mario World

By Darren Alton
"""

def Heuristic(self):
	level_end = 4830
	level_ground_ypos = 360
	mario_dead_anim = 9

	mario_x = self._Word(0xD2,0xD1)
	mario_y = self._Word(0xD4,0xD3)
	mario_anim = self._Byte(0x71)

	# dead
	if mario_anim == mario_dead_anim or mario_y > level_ground_ypos:
		return level_end

	return level_end - mario_x
