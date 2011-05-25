#!/usr/bin/env python2
from struct import unpack, Struct
from zlib import decompress, MAX_WBITS

# only supports reading at the moment.
# will probably undergo some heavy changes later to become a file-like object.
class SMVFile:
	def __init__(self, path):
		buf = open(path, 'rb').read()
		if buf[0:4] != 'SMV\x1A': raise Exception('invalid SMV magic number')

		(ver, uid, rerecords, frames)        = unpack('<IiII', buf[4:20])
		(ctrl_mask, movie_opt, sync2, sync1) = unpack('4B',    buf[20:24])
		(save_ofs, ctrl_ofs)                 = unpack('<II',   buf[24:32])

		if not(movie_opt & 1): raise Exception('SMV file uses savestates')

		self.frames = frames
		self.save = decompress(buf[save_ofs+10:ctrl_ofs], -MAX_WBITS)
		self.ctrlbuf = buf[ctrl_ofs:]

		self.players = 0
		for i in xrange(5):
			if ctrl_mask & (1 << i): self.players += 1

		if ver == 1:
			print 'SMV143 file loaded',
		elif ver == 4:
			print 'SMV151 file loaded',
			# read the new parts of the extended SMV151 header
			(input_samples,)         = unpack('<I', buf[32:36])
			(ctrl1_type, ctrl2_type) = unpack('2B', buf[36:38])
			ctrl1_ids                = unpack('4B', buf[38:42])
			ctrl2_ids                = unpack('4B', buf[42:46])
		else:
			print '[WARNING] unknown SMV version encountered'
		print 'with', self.players, 'controllers and', self.frames, 'frames'

		sync1flags = [ 'DATA_EXISTS', 'WIP1TIMING', 'LEFTRIGHT', 'VOLUMEENVX',
		               'FAKEMUTE', 'SYNCSOUND', 'HASROMINFO', 'NOCPUSHUTDOWN' ]
		if sync1 & 1:
			print 'SMV sync options:',
			for i in xrange(1,8):
				if sync1 & (1 << i): print sync1flags[i],
			print ''

		self.ctrlstruct = Struct('<' + ('H' * self.players))
		self.ctrlindex = 0

	def next_input(self):
		ret = [0] * self.players
		if self.ctrlindex <= self.frames:
			s = self.ctrlstruct
			ret = s.unpack_from(self.ctrlbuf, self.ctrlindex * s.size)
			self.ctrlindex += 1
		return ret

