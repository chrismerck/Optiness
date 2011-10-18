#!/usr/bin/env python2
import sys, pygame


from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888

#mingw_setup_args={'options': {'build_ext': {'compiler': 'mingw32'}}}
#import pyximport; pyximport.install(setup_args=mingw_setup_args)
#from xutil import snes_framebuffer_to_RGB888

if len(sys.argv) < 2: raise Exception('need argument: ./pygame-libsnes-demo [rom]')

rom = open(sys.argv[1], 'rb').read()

libsnes_path = '/usr/lib/libsnes-compatibility.so'
if sys.platform == 'win32':
	libsnes_path = '.\\libsnes-win64\\'
	libsnes_path += 'libsnes-082-fix-compat-x86_64.dll'

emu = snes_core.EmulatedSNES(libsnes_path)
emu.load_cartridge_normal(rom)

screen = pygame.display.set_mode((256, 224))

pygame.joystick.init()
joypad = pygame.joystick.Joystick(0)
joypad.init()

def input_state(port, device, index, id):
	global joypad

	if port or not(0 <= id < 12): return False # player2 or undefined button
	elif id == 4: return joypad.get_hat(0)[1] == 1
	elif id == 5: return joypad.get_hat(0)[1] == -1
	elif id == 6: return joypad.get_hat(0)[0] == -1
	elif id == 7: return joypad.get_hat(0)[0] == 1

	# button mappings here are for x360-compatible button layouts
	#            B Y e t  (skip dpad)  A X L R
	p2500_lut = [0,2,6,7, -1,-1,-1,-1, 1,3,4,5]
	return joypad.get_button(p2500_lut[id])


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
# note: we don't bother with input_poll here, so might lose a little accuracy
emu.set_input_state_cb(input_state)
emu.set_video_refresh_cb(paint_frame)

# run the emulator, frame at a time
running = True
while running:
	emu.run()
	for event in pygame.event.get():
		if event.type == pygame.QUIT: running = False

