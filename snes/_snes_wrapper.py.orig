"""
A low-level ctypes wrapper for the libsnes API.

You probably want to use the Python API in snes.core instead of this.
"""
import ctypes
from snes import exceptions as EX


# Define some ctypes data types the libsnes API uses
data_p = ctypes.POINTER(ctypes.c_ubyte)
pixel_p = ctypes.POINTER(ctypes.c_uint16)

video_refresh_cb_t = ctypes.CFUNCTYPE(None, pixel_p, ctypes.c_uint,
		ctypes.c_uint)

audio_sample_cb_t = ctypes.CFUNCTYPE(None, ctypes.c_uint16, ctypes.c_uint16)

input_poll_cb_t = ctypes.CFUNCTYPE(None)

input_state_cb_t = ctypes.CFUNCTYPE(ctypes.c_int16, ctypes.c_bool,
		ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)


class LowLevelWrapper(object):
	_lib_active = False

	def __init__(self, libname):
		self._libname = libname
		self._lib = ctypes.cdll.LoadLibrary(libname)

		# Check the self._lib version matches the API we're defining here.
		self._lib.snes_library_revision_major.restype = ctypes.c_uint
		self._lib.snes_library_revision_major.argtypes = []

		self._lib.snes_library_revision_minor.restype = ctypes.c_uint
		self._lib.snes_library_revision_minor.argtypes = []

		self.api_version = self._lib.snes_library_revision_major()
		if self.api_version != 1:
			raise EX.LibraryVersionMismatch("Unsupported libsnes API version "
					"%d.%d" % (
						self._lib.snes_library_revision_major(),
						self._lib.snes_library_revision_minor(),
					)
				)

		# Set up prototypes for all the self._lib functions.
		self._lib.snes_set_video_refresh.restype = None
		self._lib.snes_set_video_refresh.argtypes = [video_refresh_cb_t]

		self._lib.snes_set_audio_sample.restype = None
		self._lib.snes_set_audio_sample.argtypes = [audio_sample_cb_t]

		self._lib.snes_set_input_poll.restype = None
		self._lib.snes_set_input_poll.argtypes = [input_poll_cb_t]

		self._lib.snes_set_input_state.restype = None
		self._lib.snes_set_input_state.argtypes = [input_state_cb_t]

		self._lib.snes_set_controller_port_device.restype = None
		self._lib.snes_set_controller_port_device.argtypes = [
				ctypes.c_bool, ctypes.c_uint,
			]

		self._lib.snes_power.restype = None
		self._lib.snes_power.argtypes = []

		self._lib.snes_reset.restype = None
		self._lib.snes_reset.argtypes = []

		self._lib.snes_run.restype = None
		self._lib.snes_run.argtypes = []

		self._lib.snes_serialize_size.restype = ctypes.c_uint
		self._lib.snes_serialize_size.argtypes = []

		self._lib.snes_serialize.restype = ctypes.c_bool
		self._lib.snes_serialize.argtypes = [data_p, ctypes.c_uint]

		self._lib.snes_unserialize.restype = ctypes.c_bool
		self._lib.snes_unserialize.argtypes = [data_p, ctypes.c_uint]

		self._lib.snes_cheat_reset.restype = None
		self._lib.snes_cheat_reset.argtypes = []

		self._lib.snes_cheat_set.restype = None
		self._lib.snes_cheat_set.argtypes = [
				ctypes.c_uint, ctypes.c_bool, ctypes.c_char_p
			]

		self._lib.snes_load_cartridge_normal.restype = None
		self._lib.snes_load_cartridge_normal.argtypes = [
				ctypes.c_char_p, data_p, ctypes.c_uint
			]

		self._lib.snes_load_cartridge_bsx_slotted.restype = None
		self._lib.snes_load_cartridge_bsx_slotted.argtypes = [
				ctypes.c_char_p, data_p, ctypes.c_uint,
				ctypes.c_char_p, data_p, ctypes.c_uint,
			]

		self._lib.snes_load_cartridge_bsx.restype = None
		self._lib.snes_load_cartridge_bsx.argtypes = [
				ctypes.c_char_p, data_p, ctypes.c_uint,
				ctypes.c_char_p, data_p, ctypes.c_uint,
			]

		self._lib.snes_load_cartridge_sufami_turbo.restype = None
		self._lib.snes_load_cartridge_sufami_turbo.argtypes = [
				ctypes.c_char_p, data_p, ctypes.c_uint,
				ctypes.c_char_p, data_p, ctypes.c_uint,
				ctypes.c_char_p, data_p, ctypes.c_uint,
			]

		self._lib.snes_load_cartridge_super_game_boy.restype = None
		self._lib.snes_load_cartridge_super_game_boy.argtypes = [
				ctypes.c_char_p, data_p, ctypes.c_uint,
				ctypes.c_char_p, data_p, ctypes.c_uint,
			]

		self._lib.snes_unload_cartridge.restype = None
		self._lib.snes_unload_cartridge.argtypes = []

		self._lib.snes_get_region.restype = ctypes.c_bool
		self._lib.snes_get_region.argtypes = []

		self._lib.snes_get_memory_data.restype = data_p
		self._lib.snes_get_memory_data.argtypes = [ctypes.c_uint]

		self._lib.snes_get_memory_size.restype = ctypes.c_uint
		self._lib.snes_get_memory_size.argtypes = [ctypes.c_uint]

		self._lib.snes_init.restype = None
		self._lib.snes_init.argtypes = []

		self._lib.snes_term.restype = None
		self._lib.snes_term.argtypes = []

		# Now that we've configured our library, we can start it up.
		self._lib.snes_init()

		self._lib_active = True

	def close(self):
		self._lib.snes_term()
		self._lib_active = False

	def __del__(self):
		if self._lib_active:
			self.close()
