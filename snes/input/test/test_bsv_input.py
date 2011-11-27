#!/usr/bin/python
import unittest
import os.path
from StringIO import StringIO
from snes.input import bsv_input

TESTDIR = os.path.dirname(__file__)

class TestBSVDecode(unittest.TestCase):

	def test_open_from_filename(self):
		"""
		bsv_decode can read from a file.
		"""
		bsvPath = os.path.join(TESTDIR, "test.bsv")

		generator = bsv_input.bsv_decode(bsvPath)

		(serializerVersion, cartCRC, saveStateData) = generator.next()

		self.assertEqual(serializerVersion, 15)
		self.assertEqual(cartCRC, 0)
		self.assertEqual(len(saveStateData), 383968)

	def test_open_from_handle(self):
		"""
		bsv_decode can read from a file-like object.
		"""
		bsvHandle = open(os.path.join(TESTDIR, "test.bsv"), 'rb')

		generator = bsv_input.bsv_decode(bsvHandle)

		(serializerVersion, cartCRC, saveStateData) = generator.next()

		self.assertEqual(serializerVersion, 15)
		self.assertEqual(cartCRC, 0)
		self.assertEqual(len(saveStateData), 383968)

	def test_bad_magic(self):
		"""
		bsv_decode rejects files that begin with a bad magic number.
		"""
		bsvHandle = StringIO("BAD1xxxxxxxxxxxx")

		generator = bsv_input.bsv_decode(bsvHandle)

		self.assertRaisesRegexp(bsv_input.CorruptFile, "bad magic 'BAD1'",
				generator.next)

	def test_default_zeroes(self):
		"""
		bsv_decode yields zeroes after the end of the file.
		"""
		# Create a fake BSV file that contains no button press data at all.
		bsvHandle = StringIO("BSV1" + ("\0" * 12))

		generator = bsv_input.bsv_decode(bsvHandle)

		(serializerVersion, cartCRC, saveStateData) = generator.next()
		self.assertEqual(serializerVersion, 0)
		self.assertEqual(cartCRC, 0)
		self.assertEqual(saveStateData, "")

		firstRecord = generator.next()

		self.assertEqual(firstRecord, 0)


if __name__ == "__main__":
	unittest.main()
