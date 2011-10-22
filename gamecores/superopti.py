#!/usr/bin/env python2

import pygame

from skeleton_game import Game

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888 as snesfb_to_rgb

xmax = 256
ymax = 224
scale = 1

# input bits, for reference:
# 0000RLXA><v^teYB = 16-bit order
# in other words, B, Y, Se, St, ^, v, <, >, A, X, L, R = range(12)

defaultargs = {	'rom':       'smw.sfc',
				'libsnes':   'snes.dll',
				'initstate': 'smw.state',
				'inputmask': 0b000011110011 } # just the dpad and B/Y

class SuperOpti(Game):
	name = 'superopti'
	def __init__(self, args = {}):
		if args == {}: args = defaultargs
		Game.__init__(self, args)

		if 'inputmask' not in args:  args['inputmask'] = 0b111111111111
		self.GenerateValidInputs(args['inputmask'])

		# load the libsnes core and feed the emulator a ROM
		self.emu = snes_core.EmulatedSNES(args['libsnes'])
		self.emu.load_cartridge_normal(open(args['rom'], 'rb').read())

		# load a starting state if one was provided
		if 'initstate' in args:
			self.emu.unserialize(open(args['initstate'],'rb').read())

		# register drawing and input-reading callbacks
		self.emu.set_video_refresh_cb(self._video_refresh_cb)
		self.emu.set_input_state_cb(self._input_state_cb)
		# don't put anything in the work ram and framebuffer until the emulator can
		self.wram = None
		self.snesfb = None

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

	def _video_refresh_cb(self, data, width, height, hires, interlace, overscan, pitch):
		self.snesfb = (data, width, height, pitch)

	def _input_state_cb(self, port, device, index, id):
		if port or not(0 <= id < 12): return False # player2 or undefined button
		return bool(self.pad & (1 << id))

	def Freeze(self):
		return self.emu.serialize()

	def Thaw(self, state):
		self.emu.unserialize(state)

	# only convert the screen from 16-bit format to RGB888 when we need it
	def Draw(self):
		if self.snesfb is None: return None
		w,h = self.snesfb[1:3]
		# lots of copying and bitbanging overhead here; might benefit from Cython
		return pygame.image.frombuffer(snesfb_to_rgb(*self.snesfb), (w,h), 'RGB')

	def Input(self, pad):
		self.pad = pad
		self.emu.run()
		self.wram = self.emu._memory_to_string(snes_core.MEMORY_WRAM)

	# TODO: figure out a nice generic way to map RAM values to this and Victory
	def Heuristic(self):
		return 0

	def Victory(self):
		if self.wram is None: return False
		return self.wram[0xF34] > 0 # mario's score

LoadedGame = SuperOpti