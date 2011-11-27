"""
Read SNES input from a BSNES movie file (*.BSV)
"""
from struct import Struct, error as StructError


BSV_MAGIC = 'BSV1'
HEADER_STRUCT = Struct('<4s3I')
RECORD_STRUCT = Struct('<H')


class CorruptFile(Exception): pass

class CartMismatch(Exception): pass


def _extract(struct, handle):
	"""
	Read an instance of the given structure from the given file handle.
	"""
	return struct.unpack(handle.read(struct.size))


def bsv_decode(filenameOrHandle):
	"""
	Iterate the contents of the given BSV file.

	filenameOrHandle should either be a string containing the path to a BSV
	file, or a file-like object containing a BSV file.

	Once we've reached the end of the input recorded in the BSV file, we just
	yield an infinite stream of zeroes.
	"""
	# Get ourselves a handle to read from.
	if isinstance(filenameOrHandle, basestring):
		handle = open(filenameOrHandle, 'rb')
	else:
		handle = filenameOrHandle

	# Read and sanity-check the header.
	magic, serializerVersion, cartCRC, stateSize = \
			_extract(HEADER_STRUCT, handle)

	if magic != BSV_MAGIC:
		raise CorruptFile("File %r has bad magic %r, expected %r"
				% (filenameOrHandle, magic, BSV_MAGIC))

	# Let our caller know the contents of the header, in case they're
	# interested.
	stateData = handle.read(stateSize)
	yield (serializerVersion, cartCRC, stateData)

	# Start spooling out the individual button states.
	while True:
		try:
			yield _extract(RECORD_STRUCT, handle)
		except StructError:
			# We've hit the end of the file.
			break

	# After the end of the file, just keep yielding zeroes.
	while True:
		yield 0


def set_input_state_file(core, filename, restore=True, expectedCartCRC=None):
	"""
	Sets the BSV file containing the log of input states.

	!!! Also restores the savestate contained in the file !!!
	!!! unless the argument 'restore' is set to False.    !!!

	Unlike core.EmulatedSNES.set_input_state_cb, this function takes a
	filename to use, rather than a function.
	"""

	generator = bsv_decode(filename)

	def wrapper(port, device, index, id):
		return generator.next()

	(serializerVersion, cartCRC, saveStateData) = generator.next()

	if expectedCartCRC is not None:
		raise CartMismatch("Movie is for cart with CRC32 %r, expected %r"
				% (cartCRC, expectedCartCRC))

	if restore:
		core.unserialize(saveStateData)

	core.set_input_state_cb(wrapper)
