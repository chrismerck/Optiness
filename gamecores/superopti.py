#!/usr/bin/env python2

import pygame

from skeleton_game import Game

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888 as snesfb_to_rgb

defaultargs = {	'libsnes':   'snes.dll',
				'rom':       'smw.sfc',
				'initstate': 'smw.state',
				'inputmask': 0b000011110011,  # just the dpad and B/Y
				'screen':    (256, 224) }

# input bits, for reference:
# 0000RLXA><v^teYB = 16-bit order
# in other words, B, Y, Se, St, ^, v, <, >, A, X, L, R = range(12)

class SuperOpti(Game):
	name = 'superopti'

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

	def __init__(self, args = {}):
		Game.__init__(self, args, defaultargs)

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
		print 'generated', len(self.valid_inputs), 'valid inputs'

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
		self.pad = pad
		self.emu.run()
		self.wram = self.emu._memory_to_string(snes_core.MEMORY_WRAM)
		#print ord(self.wram[0xF36]),

	# TODO: figure out a nice generic way to map RAM values to this and Victory
	def Heuristic(self):
		return 0

	def Victory(self):
		if self.wram is None: return False
		return self.wram[0xF36] > 0 # mario's score

LoadedGame = SuperOpti