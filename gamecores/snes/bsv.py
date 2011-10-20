#!/usr/bin/env python2
from struct import unpack, Struct

# only supports reading at the moment.
# will probably undergo some heavy changes later to become a file-like object.
class BSVFile:
	def __init__(self, path):
		buf = open(path, 'rb').read()

		magic = buf[3::-1]  # curse you endianness!
		if magic != 'BSV1': raise Exception('invalid BSV magic number: ' + magic)

		(serializerVersion, cartCRC, stateSize) = unpack('<III', buf[4:16])

		buf = buf[16:]
		self.save = buf[:stateSize]
		self.ctrlbuf = buf[stateSize:]

		# TODO: determine number of connected controllers from savestate!
		self.players = 1

		# 16 bits per controller per frame.
		self.frames = len(self.ctrlbuf) / (2*self.players)

		print magic, 'file loaded:'
		print '  serializerVersion =', serializerVersion
		print '  cartCRC           =', cartCRC
		print '  stateSize         =', stateSize
		print 'with', self.players, 'controllers and', self.frames, 'frames'

		self.ctrlstruct = Struct('<' + ('H' * self.players))
		self.ctrlindex = 0

	def next_input(self):
		ret = [0] * self.players
		if self.ctrlindex < self.frames:
			s = self.ctrlstruct
			ret = s.unpack_from(self.ctrlbuf, self.ctrlindex * s.size)
			self.ctrlindex += 1
		return ret

