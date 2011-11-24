"""
Pygame output for SNES Video.
"""

import pygame, ctypes

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

def set_video_refresh_cb(core, callback):
	"""
	Sets the callback that will handle updated video frames.

	Unlike core.EmulatedSNES.set_video_refresh_cb, the callback passed to this
	function should accept only one parameter:
		
		"surf" is an instance of pygame.Surface containing the frame data.
	"""
	@static_var('convsurf', None)
	@static_var('subsurf', None)
	def wrapper(data, width, height, hires, interlace, overscan, pitch):
		if wrapper.convsurf is None:
			wrapper.convsurf = pygame.Surface(
				(pitch, height), depth=15, masks=(0x7c00, 0x03e0, 0x001f, 0)
			)
			wrapper.subsurf = wrapper.convsurf.subsurface((0,0,width,height))

		wrapper.convsurf.get_buffer().write(ctypes.string_at(data,pitch*height*2), 0)
		surf = wrapper.subsurf

		if hires:
			try:
				surf = pygame.transform.smoothscale(surf.convert(), (width/2,height))
			except:
				surf = pygame.transform.scale(surf, (width/2,height))

		callback(surf)

	core.set_video_refresh_cb(wrapper)
