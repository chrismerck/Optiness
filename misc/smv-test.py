#!/usr/bin/env python2
import sys, pygame

from snes import core as snes_core
from snes.video import pygame_output

from smv import SMVFile

if len(sys.argv) < 3: raise Exception('bad arguments.  smv-test [rom] [smv]')

rom = open(sys.argv[1], 'rb').read()
tas = SMVFile(sys.argv[2])

emu = snes_core.EmulatedSNES('snes9x.dll')
emu.load_cartridge_normal(data=rom) #, sram=tas.save[:2048])
pad = [0,0]

screen = pygame.display.set_mode((640, 480))
inputframe = 0

# callback functions for input and video
def poll_smv_input():
	global pad, tas, inputframe
	if 0 <= inputframe < 100: pass
	else: 
		pad = tas.next_input()
	inputframe += 1

def state_smv_input(port, device, index, id):
	global pad
	return bool(pad[0] & (0x8000 >> id))

def paint_frame(im):
	global screen
	# blit snes screen centered in pygame's display
	w,h = im.get_size()
	sw,sh = screen.get_size()
	screen.blit(im, ((sw - w)/2, (sh - h)/2))
	pygame.display.flip()


# register drawing and input-reading callbacks
emu.set_input_poll_cb(poll_smv_input)
emu.set_input_state_cb(state_smv_input)
pygame_output.set_video_refresh_cb(emu, paint_frame)

# run the emulator, frame at a time
running = True
while running:
	emu.run()
	for event in pygame.event.get():
		if event.type == pygame.QUIT: running = False

