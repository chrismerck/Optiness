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

	#mario_xvel = self._Byte(0x7B)
	#mario_yvel = self._Byte(0x7D)
	#mario_xvel_fractional = self._Byte(0x7A)
	mario_dash_timer = self._Byte(0x13E4)

	if mario_anim == mario_dead_anim or mario_y > level_ground_ypos:
		return dead

	if mario_x > level_end:
		return 0

	return (level_end - mario_x) + (0x70 - mario_dash_timer)

def Tiebreaker(self):
	mario_dash_timer = self._Byte(0x13E4)
	return mario_dash_timer
