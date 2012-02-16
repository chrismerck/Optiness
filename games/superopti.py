#!/usr/bin/env python2

import sys, os
import pygame

from common import util
from skeleton_game import Game

from snes import core as snes_core
from snes.video import pygame_output as pgvid
from snes.audio import pygame_output as pgaud
from snes.audio import wave_output as waveaud

from array import array
from ctypes import string_at

# for argument validation
def has_repeats(s):
	if len(s) > 1:
		if s[0] in s[1:]:
			return True
		return has_repeats(s[1:])
	return False

defaultargs = {	'libsnes':   'data/snes9x.dll',
				'rom':       'data/smw.sfc',
				'initstate': 'data/smw/smw_1-2.state9x',
				'heuristic': 'smw',
				'audio':     'none',
				'granularity': 10,
				'tweening':    0,
				'inputmask': '>XA', # very limited for testing purposes
				'screen':    (256, 224),
				'padoverlay': True }

validargs = { 'libsnes':     os.path.isfile,
			  'rom':         os.path.isfile,
			  'initstate':   os.path.isfile,
			  'granularity': lambda x: x > 0,
			  'tweening':    lambda x: x >= 0,
			  'inputmask':   lambda x: set(x).issubset('BY?!^v<>AXLR') and not has_repeats(x),
			  'screen':      lambda x: type(x) is tuple and (len(x) == 2) and (x[0] > 0) and (x[1] > 0),
			  'audio':       ['none', 'wave', 'pygame', 'array'],
			  'heuristic':   list(util.ListModules('heuristics')) }

class SnesPadDrawing:
	def __init__(self, alpha=255, name='SUPER NES'):
		bg = (200,200,200)
		fg = (150,150,150)
		black = (50,50,50)

		ctrlr = pygame.Surface((250,110))
		ctrlr.fill((0,0,0))
		ctrlr.set_colorkey((0,0,0))
		ctrlr.set_alpha(alpha)

		pygame.font.init()
		bold = pygame.font.Font(None,12)
		bold.set_bold(True)
		italic = pygame.font.Font(None,8)
		italic.set_italic(True)
		logo = pygame.font.Font(None,16)
		logo.set_italic(True)
		logo.set_underline(True)

		#frame
		pygame.draw.circle(ctrlr, bg, (55,55), 50)
		pygame.draw.rect(ctrlr, bg, (55,5,140,90))
		pygame.draw.circle(ctrlr, bg, (195,55), 50)
		pygame.draw.circle(ctrlr, fg, (55,55), 25, 1)
		pygame.draw.circle(ctrlr, fg, (195,55), 45)

		#dpad center
		pygame.draw.circle(ctrlr, black, (55,55), 7)

		#bayx outlines
		pygame.draw.line(ctrlr, bg, (195,74), (220,54), 21)
		pygame.draw.circle(ctrlr, bg, (195,75), 10)
		pygame.draw.circle(ctrlr, bg, (220,55), 10)
		pygame.draw.line(ctrlr, bg, (172,54), (195,36), 21)
		pygame.draw.circle(ctrlr, bg, (172,55), 10)
		pygame.draw.circle(ctrlr, bg, (195,35), 10)

		#text
		ctrlr.blit(logo.render(name, True, black), (85,10))
		ctrlr.blit(italic.render('SELECT', True, black), (94,75))
		ctrlr.blit(italic.render('START', True, black), (122,75))
		ctrlr.blit(bold.render('Y', True, bg), (155,65))
		ctrlr.blit(bold.render('B', True, bg), (176,84))
		ctrlr.blit(bold.render('X', True, bg), (209,21))
		ctrlr.blit(bold.render('A', True, bg), (230,40))

		self.frame = ctrlr

	def Draw(self, pad):
		B,Y,Se,St,Up,Down,Left,Right,A,X,L,R = [pad & (1<<i) for i in xrange(12)]

		bg = (200,200,200)
		fg = (150,150,150)
		black = (50,50,50)

		red = (100,0,150)
		yellow = red
		blue = (150,50,200)
		green = blue
		#red = (200,50,0)
		#yellow = (250,200,0)
		#blue = (0,0,200)
		#green = (50,200,0)

		ctrlr = self.frame.copy()

		#dpad
		if Up:    pygame.draw.rect(ctrlr, black, (47,35,15,20))
		if Down:  pygame.draw.rect(ctrlr, black, (47,55,15,20))
		if Left:  pygame.draw.rect(ctrlr, black, (35,47,20,15))
		if Right: pygame.draw.rect(ctrlr, black, (55,47,20,15))

		#select/start
		if Se: pygame.draw.line(ctrlr, black, (100,67), (110,60), 10)
		if St: pygame.draw.line(ctrlr, black, (125,67), (135,60), 10)

		#ba
		if B: pygame.draw.circle(ctrlr, yellow, (195,75), 8)
		if A: pygame.draw.circle(ctrlr, red, (220,55), 8)

		#yx
		if Y: pygame.draw.circle(ctrlr, green, (172,55), 8)
		if X: pygame.draw.circle(ctrlr, blue, (195,35), 8)

		#lr
		if L:
			pygame.draw.lines(ctrlr, bg, True, ((30,9), (48,3), (80,3)), 2)
			pygame.draw.lines(ctrlr, fg, False, ((30,11), (48,5), (80,5)), 1)
		if R:
			pygame.draw.lines(ctrlr, bg, True, ((168,3), (200,3), (220,9)), 2)
			pygame.draw.lines(ctrlr, fg, False, ((168,5), (200,5), (220,11)), 1)

		return ctrlr

class SuperOpti(Game):
	name = 'superopti'

	def __init__(self, args = {}):
		Game.__init__(self, args, defaultargs, validargs)
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
		pgvid.set_video_refresh_cb(self.emu, self._video_refresh_cb)
		self.emu.set_input_state_cb(self._input_state_cb)

		# unplug player 2 controller so we don't get twice as many input state callbacks
		self.emu.set_controller_port_device(snes_core.PORT_2, snes_core.DEVICE_NONE)

		# only bother with the overhead of audio if it's requested
		audtype = self.args['audio']
		if audtype == 'wave':      waveaud.set_audio_sink(self.emu, 'superopti.wav')
		elif audtype == 'pygame':  pgaud.set_audio_sample_cb(self.emu)
		elif audtype == 'array':   self.emu.set_audio_sample_cb(self._audio_sample_cb)

		# don't put anything in the work ram and framebuffer until the emulator can
		self.wram = None
		self.snesfb = None
		self.soundbuf = array('H', [])

		self._Heuristic = None
		try:
			sys.path.append('./heuristics')
			self._Heuristic = __import__(self.args['heuristic']).Heuristic
		except:
			print 'SuperOpti: could not load given heuristic, falling back to blind'

		# number of frames to let a single input persist
		self.granularity = self.args['granularity']

		# maximum length of inputs before making a new 'keyframe' state
		self.tweening = self.args['tweening']
		self.keyframe = None
		self.inputs_since_keyframe = []

		# showing what buttons are active
		self.padoverlay = None
		if self.args['padoverlay']:
			self.padoverlay = SnesPadDrawing(name='SUPEROPTI')

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

	def GenerateValidInputs(self, maskstring):
		from itertools import chain, combinations
		def powerset(iterable):
			s = list(iterable)
			return chain.from_iterable(combinations(s, r) for r in xrange(len(s)+1))

		# input bits, for reference:
		# 0000RLXA><v^!?YB = 16-bit order
		# in other words: B, Y, Se, St, Up, Down, Left, Right, A, X, L, R = range(12)
		padmap = 'BY?!^v<>AXLR'
		self.valid_inputs = []
		U,D,L,R = [1<<padmap.index(i) for i in '^v<>']

		for i in powerset(maskstring):
			pad = 0
			for j in i:
				pad |= 1<<padmap.index(j)
			if not (pad&U and pad&D) and not (pad&L and pad&R):
				self.valid_inputs.insert(0,pad)

		print 'SuperOpti: generated', len(self.valid_inputs), 'valid inputs'

	def _video_refresh_cb(self, surf):
		self.snesfb = surf

	def _input_state_cb(self, port, device, index, id):
		if port or not(0 <= id < 12): return False # player2 or undefined button
		return bool(self.pad & (1 << id))

	def _audio_sample_cb(self, left, right):
		self.soundbuf += array('H', (left,right))

	def Freeze(self):
		if self.keyframe is not None:
			return (self.keyframe, self.inputs_since_keyframe[:])
		return self.emu.serialize()

	def Thaw(self, state):
		if type(state) == tuple:
			realstate,instring = state
			tweens = len(self.inputs_since_keyframe)
			if self.keyframe == realstate and instring[:tweens] == self.inputs_since_keyframe:
				for i in instring[tweens:]:
					self.Input(i)
			else:
				self.emu.unserialize(realstate)
				self.keyframe = realstate
				self.inputs_since_keyframe = []
				for i in instring:
					self.Input(i)
		else:
			self.emu.unserialize(state)
			if self.tweening:
				self.keyframe = state
				self.inputs_since_keyframe = []

		self.wram = self.emu._memory_to_string(snes_core.MEMORY_WRAM)

	# only convert the screen from 16-bit format to RGB888 when we need it
	def Draw(self):
		# if we don't have something to draw, or if there's no point in drawing it
		if self.snesfb is None or not pygame.display.get_active():
			return None

		game_img = self.snesfb

		# draw the gamepad underneath if enabled
		if self.padoverlay is not None:
			pad_img = self.padoverlay.Draw(self.pad)
			joined = pygame.Surface(self.ScreenSize())
			joined.blit(game_img, (0,0))
			joined.blit(pad_img, (3, game_img.get_height()))
			return joined

		return game_img

	def Input(self, pad):
		# update the internal pad state that will be checked with libsnes' callbacks
		self.pad = pad

		# run for the specified number of frames on that pad state
		for i in xrange(self.granularity):
			self.emu.run()

		# do keyframe/tweening if relevant
		if self.tweening:
			if len(self.inputs_since_keyframe) >= self.tweening or self.keyframe is None:
				self.keyframe = self.emu.serialize()
				self.inputs_since_keyframe = []
			else:
				self.inputs_since_keyframe.append(pad)

		# fetch the work RAM (for heuristics to access)
		self.wram = self.emu._memory_to_string(snes_core.MEMORY_WRAM)
		if self.wram is None:
			print 'SuperOpti: error retrieving RAM'

	def _Byte(self, ofs):
		if self.wram is None:  return 0
		return ord(self.wram[ofs])

	def _Word(self, ofshi, ofslo):
		return (self._Byte(ofshi) << 8) | self._Byte(ofslo)

	def Heuristic(self):
		if self.wram is None:  return float('inf')
		if self._Heuristic is not None:  return self._Heuristic(self)
		return 1

	def Victory(self):
		return self.Heuristic() <= 0

	def Sound(self):
		tmp = self.soundbuf
		self.soundbuf = array('H', [])
		return tmp

	def ScreenSize(self):
		w,h = self.args['screen']
		if self.padoverlay is not None:
			return (w, h+self.padoverlay.frame.get_height())
		return (w,h)



LoadedGame = SuperOpti
