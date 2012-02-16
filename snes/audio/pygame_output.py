"""
Pygame output for SNES Audio.
"""

import pygame, numpy, struct

SNES_OUTPUT_FREQUENCY = 32040 # Hz

sndstruct = struct.Struct('<HH')
sndlog = ''

def set_audio_sample_cb(core, callback=pygame.mixer.Sound.play):
	"""
	Sets the callback that will handle updated audio samples.

	Unlike core.EmulatedSNES.set_audio_sample_cb, the callback passed to this
	function should accept only one parameter:

		"snd" is an instance of pygame.mixer.Sound containing the last 512
		samples.

	If no callback function is provided, the default implementation of
	snd.play() is used.
	"""

	# init pygame sound.  snes freq is 32000, 16bit unsigned stereo.
	pygame.mixer.init(
		frequency=SNES_OUTPUT_FREQUENCY,
		size=16, channels=2, buffer=512
	)

	snd = pygame.sndarray.make_sound(
			numpy.zeros( (512, 2), dtype='uint16', order='C' )
		)
	sndbuf = snd.get_buffer()

	def wrapper(left, right):
		global sndlog, sndstruct
		sndlog += sndstruct.pack(left, right)
		if len(sndlog) >= 512*2*2: # 512 stereo samples of 16-bits each
			sndbuf.write(sndlog, 0)
			sndlog = ''
			callback(snd)

	core.set_audio_sample_cb(wrapper)
