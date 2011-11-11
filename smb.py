#!/usr/bin/env python2
"""
A SuperOpti heuristic for NES Super Mario Bros.

By Darren Alton
"""

def Heuristic(self):
	dead = float('inf')
	level_end = 13*256
	level_ground_ypos = 440
	mario_dead_anim = 176
	flag_top_ypos = 176

	mario_x = self._Word(0x6d,0x86) # page*256 + position in page (0..255)
	mario_y = self._Word(0xb5,0xce)
	mario_anim = self._Byte(0x6d5)
	flag_ypos = self._Byte(0x10d)

	# is mario dead? (is his graphic table offset the position of the 'dead' tiles)
	# or did mario fall down a pit? (is his y position lower than the ground)
	if mario_anim == mario_dead_anim or mario_y > level_ground_ypos:
		return dead

	# did we reach the flagpole?
	if 0 < flag_ypos < flag_top_ypos:  return 0

	return level_end - mario_x
