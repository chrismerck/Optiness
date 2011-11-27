"""
Pygame output for SNES Video.
"""

import pygame, ctypes

convsurf = None
subsurf = None

def set_video_refresh_cb(core, callback):
	"""
	Sets the callback that will handle updated video frames.

	Unlike core.EmulatedSNES.set_video_refresh_cb, the callback passed to this
	function should accept only one parameter:
		
		"surf" is an instance of pygame.Surface containing the frame data.
	"""

	def wrapper(data, width, height, hires, interlace, overscan, pitch):
		global convsurf, subsurf
		if convsurf is None:
			convsurf = pygame.Surface(
				(pitch, height), depth=15, masks=(0x7c00, 0x03e0, 0x001f, 0)
			)
			subsurf = convsurf.subsurface((0,0,width,height))

		convsurf.get_buffer().write(ctypes.string_at(data,pitch*height*2), 0)
		surf = subsurf

		if hires or interlace:
			if hires:      width /= 2
			if interlace:  height /= 2
			try:
				surf = pygame.transform.smoothscale(surf.convert(), (width,height))
			except:
				surf = pygame.transform.scale(surf, (width,height))

		callback(surf)

	core.set_video_refresh_cb(wrapper)
