"""
A Pythonic interface to libsnes functionality.

Each emulated SNES is represented by an instance of the EmulatedSNES class. For
technical reasons, a single copy of a libsnes library can only emulate a single
SNES, therefore if you want to emulate multiple SNESs from the same Python
process, you will need multiple copies of libsnes.

To construct an EmulatedSNES object, you need to pass the name of the libsnes
implementation to load. Different platforms use different default libsnes
filenames, so if you don't have a particular one in mind, you should try the
names suggested by guess_library_name().

Constants defined in this module:

	MEMORY_* constants represent the diffent types of non-volatile storage
	a SNES cartridge can use. Not every cartridge uses every kind of storage,
	some cartridges use no storage at all. These constants are useful for
	indexing into the list returned from EmulatedSNES.unload().

	VALID_MEMORY_TYPES is a list of all the valid memory type constants.

	PORT_1 and PORT_2 constants represent the different ports to which
	controllers can be connected on the SNES. These should be passed to
	EmulatedSNES.set_controller_port_device() and will be given to the callback
	passed to EmulatedSNES.set_input_state_cb().

	DEVICE_* (but not DEVICE_ID_*) constants represent the different kinds of
	controllers that can be connected to a port. These should be passed to
	EmulatedSNES.set_controller_port_device() and will be given to the callback
	passed to EmulatedSNES.set_input_state_cb().

	DEVICE_ID_* constants represent the button and axis inputs on various
	controllers. They will be given to the callback passed to
	EmulatedSNES.set_input_state_cb().
"""
import ctypes
from snes import _snes_wrapper as W
from snes import exceptions as EX

# Constants used by this interface
MEMORY_CARTRIDGE_RAM = 0
MEMORY_CARTRIDGE_RTC = 1
MEMORY_BSX_RAM = 2
MEMORY_BSX_PRAM = 3
MEMORY_SUFAMI_TURBO_A_RAM = 4
MEMORY_SUFAMI_TURBO_B_RAM = 5
MEMORY_GAME_BOY_RAM = 6
MEMORY_GAME_BOY_RTC = 7

VALID_MEMORY_TYPES = range(8)

PORT_1 = False
PORT_2 = True

DEVICE_NONE = 0
DEVICE_JOYPAD = 1
DEVICE_MULTITAP = 2
DEVICE_MOUSE = 3
DEVICE_SUPER_SCOPE = 4
DEVICE_JUSTIFIER = 5
DEVICE_JUSTIFIERS = 6

VALID_DEVICES = range(7)

DEVICE_ID_JOYPAD_B = 0
DEVICE_ID_JOYPAD_Y = 1
DEVICE_ID_JOYPAD_SELECT = 2
DEVICE_ID_JOYPAD_START = 3
DEVICE_ID_JOYPAD_UP = 4
DEVICE_ID_JOYPAD_DOWN = 5
DEVICE_ID_JOYPAD_LEFT = 6
DEVICE_ID_JOYPAD_RIGHT = 7
DEVICE_ID_JOYPAD_A = 8
DEVICE_ID_JOYPAD_X = 9
DEVICE_ID_JOYPAD_L = 10
DEVICE_ID_JOYPAD_R = 11

DEVICE_ID_MOUSE_X = 0
DEVICE_ID_MOUSE_Y = 1
DEVICE_ID_MOUSE_LEFT = 2
DEVICE_ID_MOUSE_RIGHT = 3

DEVICE_ID_SUPER_SCOPE_X = 0
DEVICE_ID_SUPER_SCOPE_Y = 1
DEVICE_ID_SUPER_SCOPE_TRIGGER = 2
DEVICE_ID_SUPER_SCOPE_CURSOR = 3
DEVICE_ID_SUPER_SCOPE_TURBO = 4
DEVICE_ID_SUPER_SCOPE_PAUSE = 5

DEVICE_ID_JUSTIFIER_X = 0
DEVICE_ID_JUSTIFIER_Y = 1
DEVICE_ID_JUSTIFIER_TRIGGER = 2
DEVICE_ID_JUSTIFIER_START = 3

# Since a dynamic library can only be loaded once per process, we need to keep
# track of which libraries have been loaded so we don't try and load them
# twice.
_libsnes_registry = set()

def guess_library_name(tag=None):
	"""
	Yield possible names of the libsnes library.

	If tag is None or not supplied, names will be platform-appropriate
	variants of "snes" (such as "libsnes.so"), otherwise they will be
	platform-appropriate variants of "snes-%(tag)s" (such as
	"libsnes-tagname.so").

	None of the guessed names are guaranteed to exist on any particular
	platform or installation.
	"""
	if tag is None:
		tag = ""
	else:
		tag = "-" + tag

	for pattern in ["libsnes%s.so", "libsnes%s.dylib",
			"snes%s.dll"]:
		yield pattern % tag


class EmulatedSNES(W.LowLevelWrapper):
	"""
	Represents a single emulated SNES, implemented by a libsnes library.

	Once constructed, typical usage goes like this:

		1. Call the set_*_cb methods to set up the callbacks that will be
		   notified when the emulated SNES has produced a video frame, audio
		   sample, or needs controller input.
		2. Call one of the load_cartridge_* methods to give the emulated SNES
		   a cartridge image to run.
		3. Call set_controller_port_device() to connect appropriate controllers
		   to the emulated SNES.
		4. Call get_refresh_rate() to determine the intended refresh rate of
		   the loaded cartridge.
		5. Call run() to cause emulation to occur. Process the output and
		   supply input as the registered callbacks are called. For real-time
		   playback, call run() at the refresh rate returned by
		   get_refresh_rate().
		6. Call unload() to free the resources associated with the loaded
		   cartridge, and return the contents of the cartridge's non-volatile
		   storage for use with the next session.
		7. If you want to switch to a different cartridge, call
		   a load_cartridge_* method again, and go to step 3.
	"""

	# This keeps track of whether a cartridge is loaded.
	_cart_loaded = False

	# This keeps track of which cheats the user wants to apply to this game.
	_loaded_cheats = {}

	# ctypes documentation says "Make sure you keep references to CFUNCTYPE
	# objects as long as they are used from C code. ctypes doesn't, and if you
	# don't, they may be garbage collected, crashing your program when
	# a callback is made."
	#
	# So here we go.
	_video_refresh_wrapper = None
	_audio_sample_wrapper = None
	_input_poll_wrapper = None
	_input_state_wrapper = None

	def __init__(self, libname):
		"""
		Construct and return a wrapper for the given libsnes library.

		"libname" should be the platfrom appropriate filename of the libsnes
		implementation to load. If you don't have a specific filename you want
		to load, ask guess_library_name() for some likely choices.

		Raises LibraryInUse if the given library is already being used in the
		current process.
		"""
		if libname in _libsnes_registry:
			raise EX.LibraryInUse("Library %r already in use." % (libname,))
		W.LowLevelWrapper.__init__(self, libname)
		_libsnes_registry.add(libname)

		# libsnes likes to segfault if you call .run without any callbacks set,
		# so let's define some dummy ones by default.
		self.set_video_refresh_cb(lambda *args: None)
		self.set_audio_sample_cb(lambda *args: None)
		self.set_input_poll_cb(lambda: None)
		self.set_input_state_cb(lambda *args: 0)

	def _reload_cheats(self):
		"""
		Internal method.

		Reloads cheats in the emulated SNES from the _loaded_cheats variable.
		"""
		self._lib.snes_cheat_reset()

		for index, (code, enabled) in self._loaded_cheats.items():
			self._lib.snes_cheat_set(index, enabled, code)

	def _memory_to_string(self, mem_type):
		"""
		Internal method.

		Copies data from the given libsnes memory buffer into a new string.
		"""
		mem_size = self._lib.snes_get_memory_size(mem_type)
		mem_data = self._lib.snes_get_memory_data(mem_type)

		if mem_size == 0:
			return None

		buf = ctypes.create_string_buffer(mem_size)
		ctypes.memmove(buf, mem_data, mem_size)

		return buf.raw

	def _string_to_memory(self, data, mem_type):
		"""
		Internal method.

		Copies the given data into the libsnes memory buffer of the given type.
		"""
		mem_size = self._lib.snes_get_memory_size(mem_type)
		mem_data = self._lib.snes_get_memory_data(mem_type)

		if len(data) != mem_size:
			raise EX.SNESException("This cartridge requires %d bytes of "
					"memory type %d, not %d bytes" % (
						mem_size, mem_type, len(data),
					)
				)

		ctypes.memmove(mem_data, data, mem_size)

	def _require_cart_loaded(self):
		"""
		Raise an exception if a cart is not loaded.
		"""
		if not self._cart_loaded:
			raise EX.NoCartridgeLoaded("This method requires that a cartridge "
					"be loaded!")

	def _require_cart_not_loaded(self):
		"""
		Raise an exception if a cart is already loaded.
		"""
		if self._cart_loaded:
			raise EX.CartridgeAlreadyLoaded("This method requires that no "
					"cartridge be loaded!")

	# Python wrapper functions that handle all the ctypes callback casting.

	def set_video_refresh_cb(self, callback):
		"""
		Sets the callback that will handle updated video frames.

		The callback should accept the following parameters:

			"data" is a pointer to the top-left of a 512*480 array of pixels.
			Each pixel is an unsigned, 16-bit integer in XBGR1555 format.

			"width" is the number of pixels in each row of the frame. It can be
			either 256 (if the SNES is in "low-res" mode) or 512 (if the SNES
			is in "hi-res" or "psuedo-hi-res" modes).

			"height" is the number of pixel-rows in the frame. It can be 224,
			239, 448 or 478 depending on whether the SNES has "interlace"
			and/or "overscan" modes enabled.

			"hires" is True if this frame is "hi-res" or "pseudo-hi-res".

			"interlace" is True if this frame has "interlace" mode enabled.

			"overscan" is True if this frame has "overscan" mode enabled.

			"pitch" is the number of pixels from the beginning of one line to
			the beginning of the text. In non-interlaced modes, every other
			line of the frame-buffer is left blank.

		The callback should return nothing.
		"""
		def wrapped_callback(data, width, height):
			hires = (width == 512)
			interlace = (height == 448 or height == 478)
			overscan = (height == 239 or height == 478)
			pitch = 512 if interlace else 1024 # in pixels

			callback(data, width, height, hires, interlace, overscan, pitch)

		self._video_refresh_wrapper = W.video_refresh_cb_t(wrapped_callback)
		self._lib.snes_set_video_refresh(self._video_refresh_wrapper)

	def set_audio_sample_cb(self, callback):
		"""
		Sets the callback that will handle updated audio frames.

		The callback should accept the following parameters:

			"left" is an integer between 0 and 65535 that specifies the volume
			in the left audio channel.

			"right" is an integer between 0 and 65535 that specifies the volume
			in the right audio channel.

		The callback should return nothing.
		"""
		self._audio_sample_wrapper = W.audio_sample_cb_t(callback)
		self._lib.snes_set_audio_sample(self._audio_sample_wrapper)

	def set_input_poll_cb(self, callback):
		"""
		Sets the callback that will check for updated input events.

		The callback should accept no parameters and return nothing. It should
		just read new input events and store them somewhere so they can be
		returned by the input state callback.
		"""
		self._input_poll_wrapper = W.input_poll_cb_t(callback)
		self._lib.snes_set_input_poll(self._input_poll_wrapper)

	def set_input_state_cb(self, callback):
		"""
		Sets the callback that reports the current state of input devices.

		The callback may be called multiple times per frame with the same
		parameters.

		The callback will not be called if the loaded cartridge does not try to
		probe the controllers.

		The callback will not be called for a particular port if DEVICE_NONE is
		connected to it.

		The callback should accept the following parameters:

			"port" is one of the constants PORT_1 or PORT_2, describing which
			controller port is being reported.

			"device" is one of the DEVICE_* constants describing which type of
			device is currently connected to the given port.

			"index" is a number describing which of the devices connected to
			the port is being reported. It's only useful for DEVICE_MULTITAP
			and DEVICE_JUSTIFIERS - for other device types, it's always 0.

			"id" is one of the DEVICE_ID_* constants for the given device,
			describing which button or axis is being reported (for
			DEVICE_MULTITAP, use the DEVICE_ID_JOYPAD_* IDs; for
			DEVICE_JUSTIFIERS use the DEVICE_ID_JUSTIFIER_* IDs.).

		If "id" represents an analogue input (such as DEVICE_ID_MOUSE_X and
		DEVICE_ID_MOUSE_Y), you should return a value between -32768 and 32767.
		If it represents a digital input such as DEVICE_ID_MOUSE_LEFT or
		DEVICE_ID_MOUSE_RIGHT), return 1 if the button is pressed, and
		0 otherwise.

		If "id" represents an unknown input (one without a matching DEVICE_ID_*
		constant), return 0.

		You are responsible for implementing any turbo-fire features, etc.
		"""
		self._input_state_wrapper = W.input_state_cb_t(callback)
		self._lib.snes_set_input_state(self._input_state_wrapper)

	def set_controller_port_device(self, port, device):
		"""
		Connects the given device to the given controller port.

		Connecting a device to a port implicitly removes any device previously
		connected to that port. To remove a device without connecting a new
		one, pass DEVICE_NONE as the device parameter. From this point onward,
		the callback passed to set_input_state_cb() will be called with the
		appropriate device, index and id parameters.

		Whenever you call a load_cartridge_* function a DEVICE_JOYPAD will be
		connected to both ports, and devices previously connected using this
		function will be disconnected.

		It's generally safe (that is, it won't crash or segfault) to call this
		function any time, but for sensible operation, don't call it from
		inside the registered input state callback.

		"port" must be either the PORT_1 or PORT_2 constants, describing which
		port the given controller will be connected to. If "port" is set to
		"PORT_1", the "device" parameter should not be DEVICE_SUPER_SCOPE,
		DEVICE_JUSTIFIER or DEVICE_JUSTIFIERS.

		"device" must be one of the DEVICE_* (but not DEVICE_ID_*) constants,
		describing what kind of device will be connected to the given port.
		The devices are:

			- DEVICE_NONE: No device is connected to this port. The registered
			  input state callback will not be called for this port.
			- DEVICE_JOYPAD: A standard SNES gamepad.
			- DEVICE_MULTITAP: A multitap controller, which acts like
			  4 DEVICE_JOYPADs. Your input state callback will be passed "id"
			  parameters between 0 and 3.
			- DEVICE_MOUSE: A SNES mouse controller, as shipped with Mario
			  Paint.
			- DEVICE_SUPER_SCOPE: A Nintendo Super Scope light-gun device (only
			  works properly in port 2).
			- DEVICE_JUSTIFIER: A Konami Justifier light-gun device (only works
			  properly in port 2).
			- DEVICE_JUSTIFIERS: Two Konami Justifier light-gun devices,
			  daisy-chained together (only works properly in port 2). Your
			  input state callback will be passed "id" parameters 0 and 1.
		"""
		self._lib.snes_set_controller_port_device(port, device)

	def power(self):
		"""
		Turn the emulated SNES off and back on.

		Requires that a cartridge be loaded.
		"""
		self._require_cart_loaded()
		self._lib.snes_power()

	def reset(self):
		"""
		Press the front-panel Reset button on the emulated SNES.

		Requires that a cartridge be loaded.
		"""
		self._require_cart_loaded()
		self._lib.snes_reset()

	def run(self):
		"""
		Run the emulated SNES for one frame.

		Before this function returns, the registered callbacks will be called
		at least once each.

		This function should be called fifty (for PAL cartridges) or sixty (for
		NTSC cartridges) times per second for real-time emulation.

		Requires that a cartridge be loaded.
		"""
		self._require_cart_loaded()
		self._lib.snes_run()

	def unload(self):
		"""
		Remove the cartridge and return its non-volatile storage contents.

		Returns a list with an entry for each MEMORY_* constant in
		VALID_MEMORY_TYPES. If the current cartridge uses that type of storage,
		the corresponding index in the list will be a string containing the
		storage contents, which can later be passed to load_cartridge_*.
		Otherwise, the corresponding index is None.

		Requires that a cartridge be loaded.
		"""
		self._require_cart_loaded()

		res = [self._memory_to_string(t) for t in VALID_MEMORY_TYPES]
		self._lib.snes_unload_cartridge()
		self._loaded_cheats = {}
		self._cart_loaded = False
		return res

	def get_refresh_rate(self):
		"""
		Return the intended refresh-rate of the loaded cartridge.

		Returns either the integer 50 or the integer 60, depending on whether
		the loaded cartridge was designed for a 50Hz region (PAL territories)
		or a 60Hz region (NTSC territories, and Brazil's PAL60).
		"""
		region = self._lib.snes_get_region()
		if region == False:
			# NTSC, or PAL60
			return 60
		else:
			# PAL50
			return 50

	def serialize(self):
		"""
		Serializes the state of the emulated SNES to a string.

		This serialized data can be handed to unserialize() at a later time to
		resume emulation from this point.

		Requires that a cartridge be loaded.
		"""
		size = self._lib.snes_serialize_size()
		buf = ctypes.create_string_buffer(size)
		res = self._lib.snes_serialize(ctypes.cast(buf, W.data_p), size)
		if not res:
			raise EX.SNESException("problem in serialize")
		return buf.raw

	def unserialize(self, state):
		"""
		Restores the state of the emulated SNES from a string.

		Note that the cartridge's SRAM data is part of the saved state.

		Requires that the same cartridge that was loaded when serialize was
		called, be loaded before unserialize is called.
		"""
		res = self._lib.snes_unserialize(ctypes.cast(state, W.data_p),
				len(state))
		if not res:
			raise EX.SNESException("problem in unserialize")

	def cheat_add(self, index, code, enabled=True):
		"""
		Stores the given cheat code at the given index in the cheat list.

		"index" must be an integer. Only one cheat can be stored at any given
		index.

		"code" must be a string containing a valid Game Genie cheat code, or
		a sequence of them separated with plus signs like
		"DD62-3B1F+DD12-FA2C".

		"enabled" must be a boolean. It determines whether the cheat code is
		enabled or not.
		"""
		self._loaded_cheats[index] = (code, enabled)
		self._reload_cheats()

	def cheat_remove(self, index):
		"""
		Removes the cheat at the given index from the cheat list.

		"index" must be an integer previously passed to cheat_add.
		"""
		del self._loaded_cheats[index]
		self._reload_cheats()

	def cheat_set_enabled(self, index, enabled):
		"""
		Enables or disables the cheat at the given index in the cheat list.

		"index" must be an integer previously passed to cheat_add.

		"enabled" must be a boolean. It determines whether the cheat code is
		enabled or not.
		"""
		code, _ = self._loaded_cheats[index]
		self._loaded_cheats[index] = (code, enabled)
		self._reload_cheats()

	def cheat_is_enabled(self, index):
		"""
		Returns true if the cheat at the given index is enabled.

		"index" must be an integer previously passed to cheat_add.
		"""
		_, enabled = self._loaded_cheats[index]
		return enabled

	def load_cartridge_normal(self, data, sram=None, rtc=None, mapping=None):
		"""
		Load an ordinary cartridge into the emulated SNES.

		"data" must be a string containing the uncompressed, de-interleaved,
		headerless ROM image.

		"sram" should be a string containing the SRAM data saved from the
		previous session. If not supplied or None, the cartridge will be given
		a fresh, blank SRAM region (some cartridges don't use SRAM).

		"rtc" should be a string containing the real-time-clock data saved from
		the previous session. If not supplied or None, the cartridge will be
		given a fresh, blank RTC region (most cartridges don't use an RTC).

		"mapping" should be a string containing an XML document describing the
		required memory-mapping for this cartridge. If not supplied or None,
		a guessed mapping will be used (the guess should be correct for all
		licenced games released in all regions).
		"""
		self._require_cart_not_loaded()

		self._lib.snes_load_cartridge_normal(
				mapping, ctypes.cast(data, W.data_p), len(data),
			)

		self._cart_loaded = True

		if sram is not None:
			self._string_to_memory(sram, MEMORY_CARTRIDGE_RAM)

		if rtc is not None:
			self._string_to_memory(rtc, MEMORY_CARTRIDGE_RTC)

	def load_cartridge_bsx_slotted(self, base_data, slot_data=None,
			base_sram=None, base_rtc=None, base_mapping=None,
			slot_mapping=None):
		"""
		Load a BS-X slotted cartridge into the emulated SNES.

		A "BS-X slotted cartridge" is an ordinary SNES cartridge with a slot in
		the top that accepts the same memory packs that the BS-X cartridge
		does.

		"base_data" must be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the BS-X slotted cartridge.

		"slot_data" should be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the cartridge loaded inside the
		slotted cartridge's slot. If not supplied or None, the slot will be
		left empty.

		"base_sram" should be a string containing the SRAM data saved from the
		previous session. If not supplied or None, the cartridge will be given
		a fresh, blank SRAM region.

		"base_rtc" should be a string containing the real-time-clock data saved
		from the previous session. If not supplied or None, the cartridge will
		be given a fresh, blank RTC region (most cartridges don't use an RTC).

		"base_mapping" should be a string containing an XML document describing
		the memory-mapping for the BS-X slotted cartridge. If not supplied or
		None, a guessed mapping will be used (the guess should be correct for
		all licenced games released in all regions).

		"slot_mapping" should be a string containing an XML document describing
		the memory-mapping for the cartridge loaded inside the BS-X slotted
		cartridge.  If not supplied or None, a guessed mapping will be used
		(the guess should be correct for all licenced games released in all
		regions).
		"""
		self._require_cart_not_loaded()

		if slot_data is None:
			slot_length = 0
		else:
			slot_length = len(slot_data)

		self._lib.snes_load_cartridge_bsx_slotted(
				base_mapping, ctypes.cast(base_data, W.data_p), len(base_data),
				slot_mapping, ctypes.cast(slot_data, W.data_p), slot_length,
			)

		self._cart_loaded = True

		if base_sram is not None:
			self._string_to_memory(base_sram, MEMORY_CARTRIDGE_RAM)

		if base_rtc is not None:
			self._string_to_memory(base_rtc, MEMORY_CARTRIDGE_RTC)

	def load_cartridge_bsx(self, bios_data, slot_data=None, bios_ram=None,
			bios_pram=None, bios_mapping=None, slot_mapping=None):
		"""
		Load the BS-X base unit cartridge into the emulated SNES.

		The "BS-X base unit cartridge" is the one connected to the BS-X base
		unit.  It has a slot which accepts BS-X memory packs.

		"bios_data" must be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the BS-X base unit cartridge.

		"slot_data" should be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the cartridge loaded inside the
		BS-X base cartridge's slot. If not supplied or None, the slot will be
		left empty.

		"bios_ram" should be a string containing the BS-X RAM data saved from
		the previous session. If not supplied or None, the cartridge will be
		given a fresh, blank RAM region.

		"bios_pram" should be a string containing the BS-X PRAM data saved from
		the previous session. If not supplied or None, the cartridge will be
		given a fresh, blank PRAM region.

		"bios_mapping" should be a string containing an XML document describing
		the memory-mapping for the BS-X base unit cartridge. If not supplied or
		None, a guessed mapping will be used (which is accurate for the offical
		BS-X base unit cartridge).

		"slot_mapping" should be a string containing an XML document describing
		the memory-mapping for the cartridge loaded inside the BS-X base unit
		cartridge. If not supplied or None, a guessed mapping will be used (the
		guess should be correct for all licenced games released in all
		regions).
		"""
		self._require_cart_not_loaded()

		if slot_data is None:
			slot_length = 0
		else:
			slot_length = len(slot_data)

		self._lib.snes_load_cartridge_bsx(
				bios_mapping, ctypes.cast(bios_data, W.data_p), len(bios_data),
				slot_mapping, ctypes.cast(slot_data, W.data_p), slot_length,
			)

		self._cart_loaded = True

		if bios_ram is not None:
			self._string_to_memory(bios_ram, MEMORY_BSX_RAM)

		if bios_pram is not None:
			self._string_to_memory(bios_pram, MEMORY_BSX_PRAM)

	def load_cartridge_sufami_turbo(self, bios_data, slot_a_data=None,
			slot_b_data=None, slot_a_sram=None, slot_b_sram=None,
			bios_mapping=None, slot_a_mapping=None, slot_b_mapping=None):
		"""
		Load a Sufami Turbo cartridge into the emulated SNES.

		"bios_data" must be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the Sufami Turbo cartridge.

		"slot_a_data" should be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the cartridge loaded into the
		'A' slot of the Sufami Turbo cartridge. This is the actual game that
		will play.  If not supplied or left empty, no cartridge will be loaded
		in this slot.

		"slot_b_data" should be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the cartridge loaded into the
		'B' slot of the Sufami Turbo cartridge. This game's data will be
		available to the game in slot 'A'. If not supplied or left empty, no
		cartridge will be loaded in this slot.

		"slot_a_sram" should be a string containing the SRAM data saved from
		the previous time the cartridge in slot 'A' was loaded. If not supplied
		or None, the cartridge will be given a fresh, blank SRAM region.

		"slot_b_sram" should be a string containing the SRAM data saved from
		the previous time the cartridge in slot 'B' was loaded. If not supplied
		or None, the cartridge will be given a fresh, blank SRAM region.

		"bios_mapping" should be a string containing an XML document describing
		the memory-mapping for the Sufami Turbo base cartridge. If not supplied
		or None, a guessed mapping will be used (which is correct for the
		official Sufami Turbo cartridge).

		"slot_a_mapping" should be a string containing an XML document
		describing the memory-mapping for the cartridge loaded in slot 'A'.  If
		not supplied or None, a guessed mapping will be used (the guess should
		be correct for all licenced games released in all regions).

		"slot_b_mapping" should be a string containing an XML document
		describing the memory-mapping for the cartridge loaded in slot 'B'.  If
		not supplied or None, a guessed mapping will be used (the guess should
		be correct for all licenced games released in all regions).
		"""
		self._require_cart_not_loaded()

		bios_data = ctypes.cast(bios_data, W.data_p)
		bios_length = len(bios_data)

		if slot_a_data is None:
			slot_a_length = 0
		else:
			slot_a_length = len(slot_a_data)
			slot_a_data = ctypes.cast(slot_a_data, W.data_p)

		if slot_b_data is None:
			slot_b_length = 0
		else:
			slot_b_length = len(slot_b_data)
			slot_b_data = ctypes.cast(slot_b_data, W.data_p)

		self._lib.snes_load_cartridge_sufami_turbo(
				bios_mapping,   bios_data,   bios_length,
				slot_a_mapping, slot_a_data, slot_a_length,
				slot_b_mapping, slot_b_data, slot_b_length,
			)

		self._cart_loaded = True

		if slot_a_sram is not None:
			self._string_to_memory(slot_a_sram, MEMORY_SUFAMI_TURBO_A_RAM)

		if slot_b_sram is not None:
			self._string_to_memory(slot_b_sram, MEMORY_SUFAMI_TURBO_B_RAM)

	def load_cartridge_super_game_boy(self, bios_data, dmg_data=None,
			dmg_sram=None, dmg_rtc=None, bios_mapping=None, dmg_mapping=None):
		"""
		Load a Gameboy cartridge in a Super Gameboy into the emulated SNES.

		"bios_data" must be a string containing the uncompressed,
		de-interleaved, headerless ROM image of the Super Gameboy cartridge.

		"dmg_data" should be a string containing the uncompressed,
		de-interleaved, headerless ROM image of a Gameboy cartridge. The
		emulated Super Gameboy has the same compatibility with Gameboy
		cartridges as the original Super Gameboy. If not supplied or None,
		a null Gameboy cartridge will be generated and loaded into the Super
		Gameboy.

		"dmg_sram" should be a string containing the SRAM data saved from the
		previous session. If not supplied or None, the cartridge will be given
		a fresh, blank SRAM region.

		"dmg_rtc" should be a string containing the real-time-clock data saved
		from the previous session. If not supplied or None, the cartridge will
		be given a fresh, blank RTC region.

		"bios_mapping" should be a string containing an XML document describing
		the memory-mapping for the Super Gameboy cartridge. If not supplied or
		None, a guessed mapping will be used (which is correct for the official
		Super Gameboy cartridge).

		"dmg_mapping" should be a string containing an XML document describing
		the memory-mapping for the Gameboy cartridge. If not supplied or None,
		a guessed mapping will be used (which should be correct for all
		licenced games released in all regions).
		"""
		self._require_cart_not_loaded()

		if dmg_data is None:
			dmg_length = 0
		else:
			dmg_length = len(dmg_data)

		self._lib.snes_load_cartridge_super_game_boy(
				bios_mapping, ctypes.cast(bios_data, W.data_p), len(bios_data),
				dmg_mapping, ctypes.cast(dmg_data, W.data_p), dmg_length,
			)

		self._cart_loaded = True

		if dmg_sram is not None:
			self._string_to_memory(dmg_sram, MEMORY_GAME_BOY_RAM)

		if dmg_rtc is not None:
			self._string_to_memory(dmg_rtc, MEMORY_GAME_BOY_RTC)

	def get_library_info(self):
		"""
		Return the name and version numbers (major, minor) of the library.
		"""
		return [ self._lib.snes_library_id(),
		         ( self._lib.snes_library_revision_major(),
				   self._lib.snes_library_revision_minor() ) ]

	def close(self):
		"""
		Release all resources associated with this library instance.
		"""
		self._video_refresh_wrapper = None
		self._audio_sample_wrapper = None
		self._input_poll_wrapper = None
		self._input_state_wrapper = None
		W.LowLevelWrapper.close(self)
		if self._libname in _libsnes_registry:
			_libsnes_registry.remove(self._libname)
