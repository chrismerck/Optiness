#!/usr/bin/env python2
import sys, pygame

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888

from bsv import BSVFile

if len(sys.argv) < 3: raise Exception('bad arguments.  bsv-test [rom] [bsv]')

rom = open(sys.argv[1], 'rb').read()
tas = BSVFile(sys.argv[2])

emu = snes_core.EmulatedSNES('libsnes-win64\\libsnes-082-fix-compat-x86_64.dll')
emu.load_cartridge_normal(data=rom) #, sram=tas.save[:2048])

screen = pygame.display.set_mode((640, 480))
inputframe = 0

# callback functions for input and video

def state_bsv_input(port, device, index, id):
	return bool(tas.next_input()[0])

def paint_frame(data, width, height, hires, interlace, overscan, pitch):
	global screen
	# lots of copying and bitbanging overhead here.  could benefit from Cython
	im = pygame.image.frombuffer(
		snes_framebuffer_to_RGB888(data, width, height, pitch),
		(width, height), 'RGB'
	)
	# blit snes screen centered in pygame's display
	(sw,sh) = screen.get_size()
	screen.blit(im, ((sw - width)/2, (sh - height)/2))
	pygame.display.flip()


# register drawing and input-reading callbacks
#emu.set_input_poll_cb(poll_bsv_input)
emu.set_input_state_cb(state_bsv_input)
emu.set_video_refresh_cb(paint_frame)

# run the emulator, frame at a time
running = True
emu.unserialize(tas.save)
while running:
	emu.run()
	for event in pygame.event.get():
		if event.type == pygame.QUIT: running = False

