#!/usr/bin/env python2
"""
superopti heuristic for NES castlevania
"""

def Heuristic(self):
	endpoint = 20*256 # padding
	
	simonX = self._Word(0x41,0x40) # page*256 + position in page (0..255)
	simonY = self._Byte(0x3f) # may break on vertical scrolling stages in CV3
	
	simonHP = self._Byte(0x45)
	bossHP = self._Byte(0x1a9)
	
	if simonHP == 0x0: return endpoint
	if bossHP == 0x0: return 0 # beat the boss; doesn't collect orb though
	
	return (endpoint - simonX) + (simonHP - bossHP)
