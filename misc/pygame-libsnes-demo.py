#!/usr/bin/env python2
import sys, numpy, pygame

from snes import core as snes_core
from snes.util import snes_framebuffer_to_RGB888

import getopt



# libsnes library to use by default.
libsnes = '/usr/lib/libsnes-compatibility.so'
if sys.platform == 'win32':  libsnes = 'snes.dll'

# frameskip
video_frameskip = 2
video_frameskip_idx = 0

# sound buffer initialization and details.
soundbuf_idx = 0
soundbuf_size = 512

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

  -f, --frameskip
   Specify a number of video frames to skip rendering (integer)
   Default value is {}.

  -s, --soundbuf
   Specify a size (in samples) of the sound buffer to use.
   Default value is {}.

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
""".format(sys.argv[0], libsnes, video_frameskip, soundbuf_size, joymap_arg)



# parse arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hl:f:s:j:", ["help", "libsnes=", "frameskip=", "soundbuf=", "joymap="])
	if len(args) < 1:
		raise getopt.GetoptError('Must specify one ROM argument.')
	for o,a in opts:
		if o in ('-h', '--help'):
			usage()
			exit(0)
		elif o in ('-l', '--libsnes'):
			libsnes = a
		elif o in ('-f', '--frameskip'):
			video_frameskip = int(a)
		elif o in ('-s', '--soundbuf'):
			soundbuf_size = int(a)
		elif o in ('-j', '--joymap'):
			if len(a) != 12:
				raise getopt.GetoptError('--joymap must specify a string of length 12.')
			joymap_arg = a
except Exception, e:
	print str(e), usage()
	sys.exit(1)



# callback functions...
def video_refresh(data, width, height, hires, interlace, overscan, pitch):
	global video_frameskip, video_frameskip_idx
	video_frameskip_idx += 1
	if video_frameskip_idx > video_frameskip:
		video_frameskip_idx = 0
		im = pygame.image.frombuffer(
			snes_framebuffer_to_RGB888(data, width, height, pitch),
			(width, height), 'RGB'
		)
		screen.blit(im, (0,0))
		pygame.display.flip()

def audio_sample(left, right):
	global soundbuf, soundbuf_idx, soundbuf_size
	soundbuf[soundbuf_idx] = (left,right)
	soundbuf_idx += 1
	if soundbuf_idx >= soundbuf_size:
		pygame.sndarray.make_sound(soundbuf).play()
		soundbuf_idx = 0

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



# init pygame display
screen = pygame.display.set_mode((256,224))

# init pygame sound.  snes freq is 32000, 16bit unsigned stereo.
pygame.mixer.init(frequency=32000, size=16, channels=2, buffer=soundbuf_size)
soundbuf = numpy.zeros( (soundbuf_size,2), dtype='uint16', order='C' )

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
emu.set_video_refresh_cb(video_refresh)
emu.set_audio_sample_cb(audio_sample)
emu.set_input_state_cb(input_state)



# run each frame until closed.
running = True
while running:
	emu.run()
	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
