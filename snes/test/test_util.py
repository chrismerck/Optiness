#!/usr/bin/python
import unittest
from snes import util

class TestFramebufferDecoding(unittest.TestCase):

	def test_pixel_decoding(self):
		"""
		util._decode_pixel() converts SNES XRGB1555 pixels to RGB888 format.
		"""
		testdata = {
				0x0000: "\x00\x00\x00",
				0x001F: "\x00\x00\xff",
				0x03E0: "\x00\xff\x00",
				0x7C00: "\xff\x00\x00",
				0x8000: "\x00\x00\x00",
				0x7FFF: "\xff\xff\xff",
				0xFFFF: "\xff\xff\xff",
			}

		for pixel, expected in testdata.items():
			actual = util._decode_pixel(pixel)
			
			self.assertEqual(actual, expected,
					"_decode_pixel should decode %#06x to %r, not %r" %
					(pixel, expected, actual))

	def test_frame_decoding(self):
		"""
		snes_framebuffer_to_RGB888 converts SNES video frames to RGB888.
		"""
		snes_frame = [
				0x7C00, 0x03E0, # Red  Green
				0x001F, 0x0000, # Blue Black
			]

		expected_frame = (
				"\xff\x00\x00\x00\xff\x00"
				"\x00\x00\xff\x00\x00\x00"
			)

		actual_frame = util.snes_framebuffer_to_RGB888(snes_frame, 2, 2, 2)

		self.assertEqual(actual_frame, expected_frame)

	def test_frame_decoding_with_pitch(self):
		"""
		snes_framebuffer_to_RGB888 converts frames with padding on the right.
		"""
		snes_frame = [
				0x7C00, 0x03E0, 0x0000, 0x0000, # Red  Green Pad Pad
				0x001F, 0x0000, 0x0000, 0x0000, # Blue Black Pad Pad
			]

		expected_frame = (
				"\xff\x00\x00\x00\xff\x00"
				"\x00\x00\xff\x00\x00\x00"
			)

		actual_frame = util.snes_framebuffer_to_RGB888(snes_frame, 2, 2, 4)

		self.assertEqual(actual_frame, expected_frame)


if __name__ == "__main__":
	unittest.main()
