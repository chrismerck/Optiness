#!/usr/bin/env python2
"""
A pseudocode SuperOpti heuristic for NES Zelda
(trying to sketch out a way to do games more sophisticated than 'move right to win',
 the basic strategy here being a sort of piecewise-defined 'move-the-carrot' heuristic)

By Darren Alton
"""


def get_sword(self):
	return closeness_to_sword

def Heuristic(self):
	to_do_list = [ enter_cave, get_sword, go_to_level1 ]
	for i in xrange(len(to_do_list)):
		if should_use(to_do_list[i]):
			return len(to_do_list)*100 - (i*100 + to_do_list[i](self))
