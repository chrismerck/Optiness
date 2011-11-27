#!/usr/bin/python
import unittest
from PIL import Image
from snes import core, testing
from snes.test import util

class TestFrameTest(unittest.TestCase):

	def setUp(self):
		self.goodFrame = Image.open(util.TEST_GOOD_FRAME_PATH)
		self.badFrame = Image.open(util.TEST_BAD_FRAME_PATH)

	def test_no_tests(self):
		"""
		A FrameTest without data does no tests.
		"""
		ft = testing.FrameTest()

		self.assertEqual(ft.count_tests(), 0)

		testiter = ft.test(self.goodFrame)

		self.assertRaises(StopIteration, testiter.next)

	def test_video_tests_pass(self):
		"""
		A FrameTest with a video frame can pass a test.
		"""
		ft = testing.FrameTest(util.TEST_GOOD_FRAME_PATH)

		self.assertEqual(ft.count_tests(), 1)

		testiter = ft.test(self.goodFrame)

		self.assertEqual(
				testiter.next(),
				("video frame", True, ""),
			)

	def test_video_tests_fail(self):
		"""
		A FrameTest with a video frame can fail a test.
		"""
		ft = testing.FrameTest(util.TEST_GOOD_FRAME_PATH)

		self.assertEqual(ft.count_tests(), 1)

		# Make a bad frame that differs in dimensions, so that we get a string
		# difference that we can predict.
		badFrame = self.goodFrame.resize( (256, 448) )

		testiter = ft.test(badFrame)

		self.assertEqual(
				testiter.next(),
				("video frame", False,
					"Images have different sizes (256x448 vs. 256x224)"),
			)


class TestTestScript(util.SNESTestCase):

	def _make_dummy_test_script(self):
		ts = testing.TestScript()

		with open(util.TEST_ROM_PATH, "rb") as handle:
			ts.load_cartridge_normal(handle.read())

		ts.set_controllers(core.DEVICE_NONE, core.DEVICE_NONE)

		return ts

	def test_without_setup(self):
		"""
		Before configuring the SNES, TestScript.test raises exceptions.
		"""
		ts = testing.TestScript()

		# Before we've told it what cartrige to load, calling ts.test() raises
		# an exception.
		self.assertRaises(testing.TestSetupError, ts.test(self.core).next)

		with open(util.TEST_ROM_PATH, "rb") as handle:
			ts.load_cartridge_normal(handle.read())

		# Before we've told it what controllers to use, calling ts.test() still
		# raises an exception.
		self.assertRaises(testing.TestSetupError, ts.test(self.core).next)

		ts.set_controllers(core.DEVICE_NONE, core.DEVICE_NONE)

		# Now it should work.
		# FIXME: Make some assertion about the result.
		list(ts.test(self.core))

	def test_no_tests(self):
		"""
		A TestScript with no data does no tests.
		"""
		ts = self._make_dummy_test_script()

		self.assertEqual(ts.count_tests(), 0)

		testiter = ts.test(self.core)

		self.assertRaises(StopIteration, testiter.next)

	def test_frame_tests(self):
		"""
		A TestScript runs the FrameTests that have been added.
		"""
		ts = self._make_dummy_test_script()
		ts.add_frametest(60, testing.FrameTest(util.TEST_GOOD_FRAME_PATH))
		ts.add_frametest(61, testing.FrameTest(util.TEST_BAD_FRAME_PATH))

		self.assertEqual(ts.count_tests(), 2)

		results = list(ts.test(self.core))

		self.assertEqual(len(results), 2)

		# The first test should have passed.
		self.assertEqual(
				results[0],
				(60, "video frame", True, ""),
			)

		# The second test should have failed, but because it saves the output
		# images into a randomly-named directory, we can't easily test it.
		self.assertEqual(
				results[1][:3],
				(61, "video frame", False),
			)

		self.assertTrue(
				results[1][3].startswith("Image differences found."),
				results[1][3],
			)

	def test_set_controllers(self):
		"""
		TestScript.set_controllers stores the values it's given.
		"""
		ts = self._make_dummy_test_script()

		# Without arguments, no controllers are connected.
		ts.set_controllers()
		self.assertEqual(ts.port_1_device, core.DEVICE_NONE)
		self.assertEqual(ts.port_2_device, core.DEVICE_NONE)

		# With one argument, port 1 is set and port 2 is left empty.
		ts.set_controllers(core.DEVICE_JOYPAD)
		self.assertEqual(ts.port_1_device, core.DEVICE_JOYPAD)
		self.assertEqual(ts.port_2_device, core.DEVICE_NONE)

		# With two arguments, both ports are set.
		ts.set_controllers(core.DEVICE_MOUSE, core.DEVICE_SUPER_SCOPE)
		self.assertEqual(ts.port_1_device, core.DEVICE_MOUSE)
		self.assertEqual(ts.port_2_device, core.DEVICE_SUPER_SCOPE)



if __name__ == "__main__":
	unittest.main()
