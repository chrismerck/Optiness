#!/usr/bin/env python2

import pygame

from skeleton_game import Game

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888 as snesfb_to_rgb

defaultargs = {	'libsnes':   'snes.dll',
				'rom':       'smw.sfc',
				'initstate': 'smw.state',
				'granularity': 1,
#                              RLXA><v^teYB
				'inputmask': 0b000010000011, # very limited for testing purposes
				'screen':    (256, 224) }

# input bits, for reference:
# 0000RLXA><v^teYB = 16-bit order
# in other words, B, Y, Se, St, ^, v, <, >, A, X, L, R = range(12)

# Super Mario Bros. 1 notes:
# page of the level:         ord(self.wram[0x6D])
# mario's x in current page: ord(self.wram[0x86])
# mario's x in level(ish):  (ord(self.wram[0x6D]) << 8) + ord(self.wram[0x86])
class SuperOpti(Game):
	name = 'superopti'

	def __init__(self, args = {}):
		Game.__init__(self, args, defaultargs)
		self.GenerateValidInputs(args['inputmask'])

		# load the libsnes core and feed the emulator a ROM
		self.emu = snes_core.EmulatedSNES(args['libsnes'])
		self.emu.load_cartridge_normal(open(args['rom'], 'rb').read())

		# load a starting state if one was provided
		if args['initstate']:
			try:
				f = open(args['initstate'], 'rb')
				self.emu.unserialize(f.read())
			except IOError: pass

		# register drawing and input-reading callbacks
		self.emu.set_video_refresh_cb(self._video_refresh_cb)
		self.emu.set_input_state_cb(self._input_state_cb)
		# don't put anything in the work ram and framebuffer until the emulator can
		self.wram = None
		self.snesfb = None

		# number of frames to let a single input persist
		self.granularity = self.args['granularity']

	def HumanInputs(self):
		return { 'hat0_up':    0b000000010000,
				 'hat0_down':  0b000000100000,
				 'hat0_left':  0b000001000000,
				 'hat0_right': 0b000010000000,
							0: 0b000000000001,
							1: 0b000100000000,
							2: 0b000000000010,
							3: 0b001000000000,
							4: 0b010000000000,
							5: 0b100000000000,
							6: 0b000000000100,
							7: 0b000000001000  }

	def ValidInputs(self):
		return self.valid_inputs

	def GenerateValidInputs(self, mask):
		self.valid_inputs = []

		# special case.  8 directions + centered.
		dpad = []
		for du_index in xrange(3):
			du = 0b10 >> du_index
			for rl_index in xrange(3):
				rl = 0b10 >> rl_index
				dpad.append((rl << 2) | du)

		for RLXA in xrange(0b10000):
			for rldu in dpad:
				for teYB in xrange(0b10000):
					val = (RLXA << 8) | (rldu << 4) | teYB
					val = val & mask
					if val not in self.valid_inputs:
						self.valid_inputs.append(val)
		#self.valid_inputs.remove(0)
		print 'SuperOpti: generated', len(self.valid_inputs), 'valid inputs'

	def _video_refresh_cb(self, data, width, height, hires, interlace, overscan, pitch):
		self.snesfb = (data, width, height, pitch)

	def _input_state_cb(self, port, device, index, id):
		if port or not(0 <= id < 12): return False # player2 or undefined button
		return bool(self.pad & (1 << id))

	def Freeze(self):
		return self.emu.serialize()

	def Thaw(self, state):
		self.emu.unserialize(state)
		self.wram = self.emu._memory_to_string(snes_core.MEMORY_WRAM)

	# only convert the screen from 16-bit format to RGB888 when we need it
	def Draw(self):
		if self.snesfb is None: return None
		w,h = self.snesfb[1:3]
		# lots of copying and bitbanging overhead here; might benefit from Cython
		return pygame.image.frombuffer(snesfb_to_rgb(*self.snesfb), (w,h), 'RGB')

	def Input(self, pad):
		# update the internal pad state that will be checked with libsnes' callbacks
		self.pad = pad
		for i in xrange(self.granularity):  self.emu.run()
		self.wram = self.emu._memory_to_string(snes_core.MEMORY_WRAM)
		if self.wram is None: print 'SuperOpti: error retrieving RAM'
		#if ord(self.wram[0x10d]) != 0:
		#	print ord(self.wram[0x10d]), (ord(self.wram[0x6D]) << 8) + ord(self.wram[0x86])

	def _MarioPos(self):
		# is mario dead? (is his graphic table offset the position of the 'dead' tiles)
		if ord(self.wram[0x6d5]) == 176:  return 0
		# did mario fall down a pit?
		if (ord(self.wram[0xb5]) << 8) + ord(self.wram[0xce]) > 440:  return 0
		# if we reach the flagpole?
		flag = ord(self.wram[0x10d])
		if 0 < flag < 176:  return 13<<8
		# page*256 + position in page (0..255)
		return (ord(self.wram[0x6D]) << 8) + ord(self.wram[0x86])

	def _MarioPos_SMW(self):
		if ord(self.wram[0x0071]) == 9:  return 0 # dead
		return (ord(self.wram[0xD2]) << 8) + ord(self.wram[0xD1])

	# TODO: figure out a nice generic way to map RAM values to this and Victory
	def Heuristic(self):
		if self.wram is None:  return 4830 # SMB : 13<<8
		# mario's x in level(ish):
		return 4830 - self._MarioPos_SMW()

	def Victory(self):
		# mario's x position at end of 1-1
		return self.wram is not None and self._MarioPos() >= 4830 # SMB : (13<<8)

LoadedGame = SuperOpti
