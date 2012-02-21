#!/usr/bin/env python2

import sys, getopt, ctypes, struct
import pygame, numpy

from snes import core as snes_core
from snes.video import pygame_output as pgvid
from snes.audio import pygame_output as pgaud


# libsnes library to use by default.
libsnes = '/usr/lib/libsnes/libsnes-compat.so'
if sys.platform == 'win32':  libsnes = 'snes.dll'

# frameskip
screen = None

# joypad: xinput (x360) layout by default.
#             BYet^v<>AXLR
joymap_arg = '0267----1345'



def usage():
	global libsnes, video_frameskip, soundbuf_size, joymap_arg
	return """
Usage:
 python {} [options] rom.sfc [save.srm]

  -h, --help
   Display this help message.

  -l, --libsnes
   Specify the dynamically linked LibSNES library to use.
   If unspecified, {} is used by default.

  -j, --joymap
   Specify a mapping of SNES inputs to PC joypad buttons.
   This must be a string of 12 characters, specifying which
   PC joypad button to check for each SNES button, in the order:
    B, Y, Select, Start, Up, Down, Left, Right, A, X, L, R.
   Non-numerals are ignored.  Only buttons 0-9 are supported.
   If buttons are mapped to the D-pad, they will be used, but
   the first POV hat on the joypad is also mapped to the D-pad.
   The default string is suitable for Xbox controllers: {}

  rom.sfc
   The ROM file to load.  Must be specified after all options.

  save.srm
   The SRAM to load (optional).  Must be specified after the ROM.
   Warning: Won't be updated or overwritten during or after emulation.
""".format(sys.argv[0], libsnes, joymap_arg)



# parse arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hl:f:s:j:", ["help", "libsnes=", "joymap="])
	if len(args) < 1:
		raise getopt.GetoptError('Must specify one ROM argument.')
	for o,a in opts:
		if o in ('-h', '--help'):
			usage()
			exit(0)
		elif o in ('-l', '--libsnes'):
			libsnes = a
		elif o in ('-j', '--joymap'):
			if len(a) != 12:
				raise getopt.GetoptError('--joymap must specify a string of length 12.')
			joymap_arg = a
except Exception, e:
	print str(e), usage()
	sys.exit(1)



def paint_frame(surf):
	global screen, start

	if screen is None:
		screen = pygame.display.set_mode(surf.get_size())

	screen.blit(surf, (0,0))
	pygame.display.flip()



def input_state(port, device, index, id):
	global joymap
	ret = False

	# we're only interested in player 1
	if not port and 0 <= id < 12:
		# pov hat as fallback for d-pad (up, down, left, right)
		if   id == 4:  ret |= joypad.get_hat(0)[1] == 1
		elif id == 5:  ret |= joypad.get_hat(0)[1] == -1
		elif id == 6:  ret |= joypad.get_hat(0)[0] == -1
		elif id == 7:  ret |= joypad.get_hat(0)[0] == 1

		tmp = joymap[id]
		if tmp >= 0:
			ret |= joypad.get_button(tmp)

	return ret



# map snes buttons to joybuttons
# we want a mapping of "joymap[x] = y", where:
#  x = the snes button id
#  y = the joypad button corresponding to x
joymap = [-1] * 12
for i in xrange(12):
	button = joymap_arg[i]
	if button in '0123456789':
		joymap[i] = int(button)



# init pygame joypad input
pygame.joystick.init()
joypad = pygame.joystick.Joystick(0)
joypad.init()

# pygame 'clock' used to limit to 60fps on fast computers
clock = pygame.time.Clock()



# load game and init emulator
rom = open(args[0], 'rb').read()
sram = None
if len(args) > 1:
	sram = open(args[1], 'rb').read()

emu = snes_core.EmulatedSNES(libsnes)
emu.load_cartridge_normal(rom, sram)

# register callbacks
pgvid.set_video_refresh_cb(emu, paint_frame)
pgaud.set_audio_sample_cb(emu)
emu.set_input_state_cb(input_state)

# unplug player 2 controller so we don't get twice as many input state callbacks
emu.set_controller_port_device(snes_core.PORT_2, snes_core.DEVICE_NONE)

# run each frame until closed.
running = True
while running:
	emu.run()
	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_F2:
				open('emu.state', 'wb').write(emu.serialize())
			elif event.key == pygame.K_F4:
				emu.unserialize(open('emu.state', 'rb').read())

