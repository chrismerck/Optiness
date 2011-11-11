#!/usr/bin/env python2
import sys, numpy, pygame

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888

import getopt

def usage():
	print """
python {} [-h] [-j (joypad mapping)] [-l (libsnes.so)] rom.sfc

  -h, --help
    Display this help message.


  -j, --joymap
    Specify a mapping of SNES inputs to PC joypad buttons.

    This must be a string of 12 characters, specifying which
    PC joypad button to check for each SNES button, in the order:

    B, Y, Select, Start, Up, Down, Left, Right, A, X, L, R.

    Non-numerals are ignored.  Only buttons 0-9 are supported.
    The default string is suitable for Xbox gamepads: 0267----1345

    If buttons are mapped to the D-pad, they will be used, but
    the first POV hat on the joypad is also mapped to the D-pad.


  -l, --libsnes
    Specify the dynamically linked LibSNES library to use.


  rom.sfc
    The ROM file to load.  Must be specified after all options.
""".format(sys.argv[0])

# libsnes library to use by default.
libsnes = '/usr/lib/libsnes-compatibility.so'
if sys.platform == 'win32':  libsnes = 'snes.dll'

# xinput (x360) layout by default.
#             BYet^v<>AXLR
joymap_arg = '0267----1345'

# sound buffer initialization and details.
soundbuf_idx = 0
soundbuf_size = 512
soundbuf = numpy.zeros( (soundbuf_size,2), dtype='uint16', order='C' )


# callback functions...
def video_refresh(data, width, height, hires, interlace, overscan, pitch):
	im = pygame.image.frombuffer(
		snes_framebuffer_to_RGB888(data, width, height, pitch),
		(width, height), 'RGB'
	)
	screen.blit(im, (0,0))
	pygame.display.flip()

def audio_sample(left, right):
	global soundbuf, soundbuf_idx, soundbuf_size
	if soundbuf_idx >= soundbuf_size:
		pygame.sndarray.make_sound(soundbuf).play()
		soundbuf_idx = 0
	else:
		soundbuf[soundbuf_idx] = (left,right)
		soundbuf_idx += 1

def input_state(port, device, index, id):
	if port or not(0 <= id < 12): return False # player2 or undefined button

	ret = False

	# pov hat as fallback for d-pad
	if id == 4:    ret = joypad.get_hat(0)[1] == 1
	elif id == 5:  ret = joypad.get_hat(0)[1] == -1
	elif id == 6:  ret = joypad.get_hat(0)[0] == -1
	elif id == 7:  ret = joypad.get_hat(0)[0] == 1

	tmp = joymap[id]
	if tmp >= 0:
		ret |= joypad.get_button(tmp)

	return ret



# parse arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hj:l:", ["help", "joymap=", "libsnes="])
except getopt.GetoptError, err:
	print str(err)
	usage()
	sys.exit(1)

# process arguments
for o,a in opts:
	if o in ('-h', '--help'):
		usage()
		exit(0)
	elif o in ('-j', '--joymap'):
		if len(a) != 12:
			print o, 'must specify a string of length 12.'
			exit(2)
		joymap = a
	elif o in ('-l', '--libsnes'):
		libsnes = a

# map snes buttons to joybuttons
pygame.joystick.init()
joypad = pygame.joystick.Joystick(0)
joypad.init()

# we want a mapping of "joymap[x] = y", where:
#  x = the snes button id
#  y = the joypad button corresponding to x
joymap = [-1] * 12
for i in xrange(12):
	button = joymap_arg[i]
	if button in '0123456789':
		joymap[i] = int(button)


# init pygame display
screen = pygame.display.set_mode((256,224))

# init pygame sound.  snes freq is 32000, 16bit unsigned stereo.
pygame.mixer.init(frequency=32000, size=16, channels=2, buffer=soundbuf_size)

# load rom and init emulator
rom = open(args[0], 'rb').read()
emu = snes_core.EmulatedSNES(libsnes)
emu.load_cartridge_normal(rom)

# register callbacks
emu.set_input_state_cb(input_state)
emu.set_video_refresh_cb(video_refresh)
emu.set_audio_sample_cb(audio_sample)

# used to limit to 60fps on fast computers
clock = pygame.time.Clock()

# run each frame until closed.
running = True
while running:
	emu.run()
	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
