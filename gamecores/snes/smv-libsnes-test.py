#!/usr/bin/env python2
import sys, pygame

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888

from smv import SMVFile

if len(sys.argv) < 3: raise Exception('bad arguments.  smv-test [rom] [smv]')

rom = open(sys.argv[1], 'rb').read()
tas = SMVFile(sys.argv[2])

emu = snes_core.EmulatedSNES('/usr/lib/libsnes-snes9x.so')
emu.load_cartridge_normal(data=rom) #, sram=tas.save[:2048])
pad = [0,0]

screen = pygame.display.set_mode((640, 480))
inputframe = 0

# callback functions for input and video
def poll_smv_input():
	# TODO: figure out why the timing doesn't seem to work.
	global pad, tas, inputframe
	if 0 <= inputframe < 2: pass
	else: 
		pad = tas.next_input()
	inputframe += 1

def state_smv_input(port, device, index, id):
	global pad
	return bool(pad[0] & (0x8000 >> id))

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
emu.set_input_poll_cb(poll_smv_input)
emu.set_input_state_cb(state_smv_input)
emu.set_video_refresh_cb(paint_frame)

# run the emulator, frame at a time
running = True
while running:
	emu.run()
	for event in pygame.event.get():
		if event.type == pygame.QUIT: running = False

