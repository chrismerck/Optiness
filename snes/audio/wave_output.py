"""
.wav output for SNES audio.
"""
import wave
import struct
from itertools import izip
from tempfile import mkstemp
import os
import os.path

SNES_OUTPUT_FREQUENCY = 32040 # Hz

# libsnes generates signed 16-bit samples, but passes them to us marked as
# uint16 values so we need to pack them as uint16 values to avoid any
# signed/unsigned conversions.
sndstruct = struct.Struct('<HH')


def set_audio_sink(core, filenameOrHandle):
	"""
	Records SNES audio to the given .wav file.

	"core" should be an instance of snes.core.EmulatedSNES.

	"filenameOrHandle" should be either a string representing the filename
	where audio data should be written, or a file-handle opened in "wb" mode.

	Audio data will be written to the given file as a 32040Hz 16-bit stereo
	.wav file, using the 'wave' module from the Python standard library.

	Returns the wave.Wave_write instance used to write the SNES audio.
	"""
	res = wave.open(filenameOrHandle, "wb")
	res.setnchannels(2)
	res.setsampwidth(2)
	res.setframerate(SNES_OUTPUT_FREQUENCY)
	res.setcomptype('NONE', 'not compressed')

	def audio_sample(left, right):
		# We can safely use .writeframesraw() here because the header will be
		# corrected once we call .close()
		res.writeframesraw(sndstruct.pack(left, right))

	core.set_audio_sample_cb(audio_sample)

	return res

