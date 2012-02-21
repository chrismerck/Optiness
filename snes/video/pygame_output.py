"""
Pygame output for SNES Video.
"""

import pygame, ctypes

OUTPUT_WIDTH=256
OUTPUT_HEIGHT=239

def set_video_refresh_cb(core, callback):
	"""
	Sets the callback that will handle updated video frames.

	Unlike core.EmulatedSNES.set_video_refresh_cb, the callback passed to this
	function should accept only one parameter:

		"surf" is an instance of pygame.Surface containing the frame data.
	"""

	def wrapper(data, width, height, hires, interlace, overscan, pitch):
		convsurf = pygame.Surface(
			(pitch, height), depth=15, masks=(0x7c00, 0x03e0, 0x001f, 0)
		)
		surf = convsurf.subsurface((0,0,width,height))

		# this try-except block works around a bug in pygame 1.9.1 on 64-bit hosts.
		# http://archives.seul.org/pygame/users/Apr-2011/msg00069.html
		# https://bitbucket.org/pygame/pygame/issue/109/bufferproxy-indexerror-exception-thrown
		try:
			convsurf.get_buffer().write(ctypes.string_at(data,pitch*height*2), 0)
		except IndexError:
			return

		tryScale = False

		if hires:
			width /= 2
			tryScale = True

		if interlace:
			height /= 2
			tryScale = True

		if tryScale:
			try:
				surf = pygame.transform.smoothscale(surf.convert(),
						(width,height))
			except:
				surf = pygame.transform.scale(surf,
						(width,height))

		callback(surf)

	core.set_video_refresh_cb(wrapper)

