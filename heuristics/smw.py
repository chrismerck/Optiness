#!/usr/bin/env python2
"""
A SuperOpti heuristic for SNES Super Mario World

By Darren Alton
"""

def Heuristic(self):
	dead = float('inf')

	level_ground_ypos = 380
	mario_dead_anim = 9

	level_screen_count = self._Byte(0x05D)
	level_finished_timer = self._Byte(0x1493)  # this byte is set to 255 when the goal is reached

	mario_x = self._Word(0xD2,0xD1)
	mario_y = self._Word(0xD4,0xD3)
	mario_anim = self._Byte(0x71)
	mario_dash_timer = self._Byte(0x13E4)

	#mario_xvel = self._Byte(0x7B)
	#mario_yvel = self._Byte(0x7D)
	#mario_xvel_fractional = self._Byte(0x7A)

	# this should be a general estimate of where the goal tape is for most levels
	level_goal_position = (level_screen_count-1)*256

	if mario_anim == mario_dead_anim or mario_y > level_ground_ypos:
		return dead

	# are we in the end-of-level marching sequence?
	if level_finished_timer > 0:
		return 0

	return (level_goal_position - mario_x) + (0x70 - mario_dash_timer)
