"""
Calculate the on-screen dimensions of the SNES frame.
"""

# Numbers stolen from bsnes.
NTSC_ASPECT = 54.0 / 47.0
PAL_ASPECT = 32.0 / 23.0

# The SNES also has a 512px hi-res mode, but it does not change the width of
# the image on-screen, so we can do all our calculations for the 256px image.
SNES_WIDTH = 256
SNES_HEIGHT = 240

def scale_max(windowW, windowH, imageW, imageH, integerOnly=False):
	"""
	Scale the image as large as possible, regardless of aspect ratio.
	"""
	if imageH > SNES_HEIGHT:
		imageH = imageH // 2

	if integerOnly and windowW > SNES_WIDTH:
		width = (windowW // SNES_WIDTH) * SNES_WIDTH
	else:
		width = windowW
		
	if integerOnly and windowH > imageH:
		height = (windowH // imageH) * imageH
	else:
		height = windowH

	return width, height

def scale_with_aspect(windowW, windowH, imageW, imageH, aspect=1.0,
		integerOnly=False):
	"""
	Scale the image as large as possible, after aspect-ratio correction.

	The aspect-ratio correction just multiplies the width; it's not exactly
	what you'd expect from the name "aspect ratio" but it's what bsnes does,
	and it's about the only sensible thing to do given that the SNES has output
	modes of varying height that don't change the effective width.
	"""
	if imageH > SNES_HEIGHT:
		imageH = imageH // 2

	multiplier = min(
			float(windowW) / (SNES_WIDTH * aspect),
			float(windowH) / SNES_HEIGHT,
		)

	if integerOnly and windowW > SNES_WIDTH * aspect and windowH > SNES_HEIGHT:
		multiplier = int(multiplier)

	return int(SNES_WIDTH * aspect * multiplier), int(imageH * multiplier)

def scale_raw(windowW, windowH, imageW, imageH, integerOnly=False):
	"""
	Scale the image as large possible, maintaining a 1:1 pixel ratio.
	"""
	return scale_with_aspect(windowW, windowH, imageW, imageH, 1.0,
			integerOnly)

def scale_ntsc(windowW, windowH, imageW, imageH, integerOnly=False):
	"""
	Scale the image as large possible, matching the NTSC aspect ratio.
	"""
	return scale_with_aspect(windowW, windowH, imageW, imageH, NTSC_ASPECT,
			integerOnly)

def scale_pal(windowW, windowH, imageW, imageH, integerOnly=False):
	"""
	Scale the image as large possible, matching the PAL aspect ratio.
	"""
	return scale_with_aspect(windowW, windowH, imageW, imageH, PAL_ASPECT,
			integerOnly)
