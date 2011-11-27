#!/usr/bin/python
import unittest
from snes import exceptions as EX
from snes.test import util

class TestSNESCore(util.SNESTestCase):
	"""
	Call as much of libsnes as we can.

	This largely checks we have our calling conventions correct, but it's also
	useful for testing any sanity-checking in snes.core.
	"""

	def test_video_callback_called(self):
		"""
		Video callback is called once per frame.
		"""
		results = []
		def video_refresh(data, width, height, *args):
			results.append("Got a video frame %dx%d" %
					(width, height))
		self.core.set_video_refresh_cb(video_refresh)

		self._loadTestCart()

		for _ in range(3):
			self.core.run()

		self.assertEqual(results, [
				"Got a video frame 256x224",
				"Got a video frame 256x224",
				"Got a video frame 256x224",
			])

	def test_audio_callback_called(self):
		"""
		Audio callback is called once for each audio sample.
		"""
		results = [0]
		def audio_sample(left, right):
			results[0] += 1
		self.core.set_audio_sample_cb(audio_sample)

		self._loadTestCart()
		self.core.run()
		self.assertEqual(results[0], 490)
		self.core.run()
		self.assertEqual(results[0], 1023)

	# TODO: Check set_input_poll_cb if we figure out whether the callback is
	# supposed to be called even if the running SNES software isn't asking for
	# input.
	
	# TODO: Check set_input_state_cb if we can find a public-domain test ROM
	# that polls for input.
	
	def test_power(self):
		"""
		We can hard-reset without crashing.
		"""
		# Power-cycling with no ROM loaded segfaults libsnes, so protect
		# against it.
		self.assertRaises(EX.NoCartridgeLoaded, self.core.power)

		# Try power-cycling with a ROM loaded.
		self._loadTestCart()
		self.core.power()

		# Even after a few frames?
		self.core.run()
		self.core.run()
		self.core.run()
		self.core.power()

	def test_reset(self):
		"""
		We can soft-reset without crashing.
		"""
		# Resetting with no ROM loaded segfaults libsnes, so protect
		# against it.
		self.assertRaises(EX.NoCartridgeLoaded, self.core.reset)

		# Try resetting with a ROM loaded.
		self._loadTestCart()
		self.core.reset()

		# Even after a few frames?
		self.core.run()
		self.core.run()
		self.core.run()
		self.core.reset()

	def test_run(self):
		"""
		We can run a single frame without crashing.
		"""
		# Running the SNES with no ROM loaded segfaults libsnes, so protect
		# against it.
		self.assertRaises(EX.NoCartridgeLoaded, self.core.run)

		# After loading a ROM, we can run frames.
		self._loadTestCart()
		self.core.run()

	def test_unload(self):
		"""
		We can unload a loaded cart without crashing.
		"""
		# Before a cartridge is loaded, we can't unload anything.
		self.assertRaises(EX.NoCartridgeLoaded, self.core.unload)

		# After loading a cart, we can unload it.
		self._loadTestCart()
		memory = self.core.unload()

		# Our test-cart doesn't use any non-volatile storage, so unload()
		# shouldn't return anything.
		self.assertEqual(memory,
				[None, None, None, None, None, None, None, None],
			)

		# After unloading a cart, things that require a loaded cart should
		# complain.
		self.assertRaises(EX.NoCartridgeLoaded, self.core.run)

	def test_get_refresh_rate(self):
		"""
		libsnes recognises the test rom as 60Hz.
		"""
		self._loadTestCart()
		self.assertEqual(
				self.core.get_refresh_rate(),
				60,
			)

	def test_get_library_info(self):
		"""
		libsnes can identify itself with plausible info.
		"""
		name, (revMajor, revMinor) = self.core.get_library_info()

		self.assertTrue(isinstance(name, str),
				"Name should be string, not %r" % (name,))
		self.assertTrue(isinstance(revMajor, long),
				"Major revision should be int, not %r" % (revMajor,))
		self.assertTrue(isinstance(revMinor, long),
				"Minor revision should be int, not %r" % (revMinor,))


if __name__ == "__main__":
	unittest.main()
