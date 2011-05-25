class SNESException(Exception):
	"""
	Something went wrong with libsnes.
	"""

class NoCartridgeLoaded(SNESException):
	"""
	Can't do this without a loaded cartridge.
	"""

class CartridgeAlreadyLoaded(SNESException):
	"""
	Can't do this with a loaded cartridge.
	"""

class LibraryInUse(SNESException):
	"""
	The requested library is already being used by something else.
	"""

class LibraryVersionMismatch(SNESException):
	"""
	The library version is one we don't recognise.
	"""
