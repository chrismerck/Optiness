#!/usr/bin/python
import unittest
from snes.video import scaling

class ScalingMethodTestCase(unittest.TestCase):

	def _scale_image(self, windowW, windowH, imageW, imageH,
			integerOnly=False):
		raise NotImplementedError

	def assertScalingSize(self, windowSize, base_height, expectedSize,
			integerOnly=False):
		windowW, windowH = windowSize
		expectedW, expectedH = expectedSize

		for imageW in (256, 512): # hi-res mode
			for height_multiplier in (1, 2): # interlace mode
				imageH = base_height * height_multiplier
				actualW, actualH = self._scale_image(
						windowW, windowH,
						imageW, imageH,
						integerOnly,
					)

				self.assertEqual(actualW, expectedW)
				self.assertEqual(actualH, expectedH)


class TestScaleMax(ScalingMethodTestCase):

	def _scale_image(self, *args, **kwargs):
		return scaling.scale_max(*args, **kwargs)

	def test_scale_up(self):
		"""
		scale_max stretches the image up to the full window size.

		...regardless of window aspect ratio, or image size.
		"""
		self.assertScalingSize( (1000, 800), 224, (1000, 800) )
		self.assertScalingSize( (1000, 800), 239, (1000, 800) )

		self.assertScalingSize( (800, 1000), 224, (800, 1000) )
		self.assertScalingSize( (800, 1000), 239, (800, 1000) )

	def test_scale_down(self):
		"""
		scale_max squishes the image down to the full window size.

		...regardless of window aspect ratio or image size.
		"""
		self.assertScalingSize( (100, 80), 224, (100, 80) )
		self.assertScalingSize( (100, 80), 239, (100, 80) )

		self.assertScalingSize( (80, 100), 224, (80, 100) )
		self.assertScalingSize( (80, 100), 239, (80, 100) )

	def test_integer_scale_up(self):
		"""
		In integerOnly mode, scale_max uses the largest multiplier that fits.

		It doesn't contstrain the horizontal and vertical multipliers to be the
		same, though.
		"""
		self.assertScalingSize( (800, 800), 224, (256 * 3, 224 * 3), True )
		self.assertScalingSize( (800, 800), 239, (256 * 3, 239 * 3), True )

		self.assertScalingSize( (800, 600), 224, (256 * 3, 224 * 2), True )
		self.assertScalingSize( (800, 600), 239, (256 * 3, 239 * 2), True )

	def test_integer_scale_down(self):
		"""
		If a window dimension is smaller than the image, ignore "integerOnly".

		"integerOnly" should still affect any window dimensions that are larger
		than the image, though.
		"""
		self.assertScalingSize( (800, 150), 224, (256 * 3, 150), True )
		self.assertScalingSize( (800, 150), 239, (256 * 3, 150), True )

		self.assertScalingSize( (150, 800), 224, (150, 224 * 3), True )
		self.assertScalingSize( (150, 800), 239, (150, 239 * 3), True )

		self.assertScalingSize( (150, 150), 224, (150, 150), True )
		self.assertScalingSize( (150, 150), 239, (150, 150), True )


class TestScaleRaw(ScalingMethodTestCase):

	def _scale_image(self, *args, **kwargs):
		return scaling.scale_raw(*args, **kwargs)

	def test_scale_up(self):
		self.assertScalingSize( (800, 1000), 224, (800, 700) )
		self.assertScalingSize( (800, 1000), 239, (800, 746) )

		self.assertScalingSize( (1000, 800), 224, (853, 746) )
		self.assertScalingSize( (1000, 800), 239, (853, 796) )

	def test_scale_down(self):
		self.assertScalingSize( (200, 300), 224, (200, 175) )
		self.assertScalingSize( (200, 300), 239, (200, 186) )

		self.assertScalingSize( (300, 200), 224, (213, 186) )
		self.assertScalingSize( (300, 200), 239, (213, 199) )

	def test_integer_scale_up(self):
		self.assertScalingSize( (700, 1000), 224, (512, 448), True)
		self.assertScalingSize( (700, 1000), 239, (512, 478), True)

		# 700px vertically is enough to display 3x224 = 672, but not enough to
		# display 3x240 = 720. Therefore we pick the smaller multiplier, so
		# that no matter what video mode the SNES is in, we won't have to
		# suddenly jump to a smaller multiplier.
		self.assertScalingSize( (1000, 700), 224, (512, 448), True)
		self.assertScalingSize( (1000, 700), 239, (512, 478), True)

	def test_integer_scale_down(self):
		"""
		If a window dimension is smaller than the image, ignore "integerOnly".
		"""
		self.assertScalingSize( (200, 300), 224, (200, 175), True )
		self.assertScalingSize( (200, 300), 239, (200, 186), True )

		self.assertScalingSize( (300, 200), 224, (213, 186), True )
		self.assertScalingSize( (300, 200), 239, (213, 199), True )


if __name__ == "__main__":
	unittest.main()
