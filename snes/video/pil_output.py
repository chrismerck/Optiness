"""
Python Imaging Library (PIL) output for SNES Video.
"""

from tempfile import mkdtemp
import os.path
from PIL import Image
from snes.util import snes_framebuffer_to_RGB888

def _snes_to_image(data, width, height, hires, interlace, overscan, pitch):
	return Image.fromstring("RGB", (width, height),
			snes_framebuffer_to_RGB888(data, width, height, pitch))

def set_video_refresh_cb(core, callback):
	"""
	Sets the callback that will handle updated video frames.

	Unlike core.EmulatedSNES.set_video_refresh_cb, the callback passed to this
	function should accept only one parameter:
		
		"image" is an instance of PIL.Image containing the frame data.
	"""
	def wrapper(*args):
		callback(_snes_to_image(*args))

	core.set_video_refresh_cb(wrapper)

def image_difference(imageA, imageB):
	"""
	Determine the differences (if any) between two images.

	"imageA" and "imageB" should be PIL Image objects.

	If the images are identical, returns None.

	If the images differ in mode or size, returns a string describing the
	differences. Note: if one image is exactly twice the width of the other,
	the smaller image is resized to the width of the larger before comparing
	dimensions. This is because some libsnes implementations render non-hires
	frames at 256px wide, and some render them at 512px wide.

	If the images differ in pixel data, returns a 1-bit Image with the same
	dimensions as the input images. Where the two source images have different
	pixel values, those pixels are set to "1" in the resulting image while all
	the equal pixels are set to "0".
	"""
	# If the images are in different modes (colour-spaces) then they're
	# different.
	if imageA.mode != imageB.mode:
		return "Images have different modes (%r vs. %r)" % (
				imageA.mode, imageB.mode,
			)

	# bsnes' accuracy core outputs 512px-per-line at all times (as does the
	# real SNES, technically) while most cores output 256px-per-line normally
	# and 512px-per-line in hi-res mode. This difference is not necessarily
	# a useful difference, so if one image is exactly twice as wide as the
	# other, we'll resize the smaller to the width of the larger.
	widthA, heightA = imageA.size
	widthB, heightB = imageB.size

	if widthA == 2 * widthB:
		imageB = imageB.resize( (widthA, heightB ) )
	elif widthB == 2 * widthA:
		imageA = imageA.resize( (widthB, heightA ) )

	# If images have different dimensions (modulo the resizing above), then
	# they're different.
	if imageA.size != imageB.size:
		return "Images have different sizes (%dx%d vs. %dx%d)" % (
				imageA.size[0], imageA.size[1],
				imageB.size[0], imageB.size[1],
			)

	# Before we start pixel-poking, let's let Python figure out whether there's
	# any image differences.
	imageAstr = imageA.tostring()
	imageBstr = imageB.tostring()

	if imageAstr == imageBstr:
		return None

	# We know these images are different, we just have to figure out where.
	diffMap = Image.new("1", imageA.size)

	pixelsA = imageA.load()
	pixelsB = imageB.load()
	pixelsDiff = diffMap.load()
	width, height = imageA.size

	for y in xrange(height):
		for x in xrange(width):
			if pixelsA[x,y] != pixelsB[x,y]:
				pixelsDiff[x,y] = 1
			else:
				pixelsDiff[x,y] = 0

	return diffMap

def describe_difference(imageA, imageB):
	"""
	Describe the differences (if any) between two images.

	"imageA" and "imageB" should be PIL Image objects.

	If the images are identical, returns None.

	If the images differ in any way, returns a string describing the
	differences. In situations where image_difference() would return a string,
	this function returns the same string. In situations where
	image_difference() would return a difference map image, this function
	saves imageA, imageB and the difference map to a newly created directory,
	and returns a string that describes their filenames.
	"""
	difference = image_difference(imageA, imageB)

	if difference is None:
		# No differences.
		return

	if isinstance(difference, Image.Image):
		# Save the comparators and result so that we can examine them at
		# our leisure.
		outputdir = mkdtemp()
		actual_name = os.path.join(outputdir, "actual.png")
		expected_name = os.path.join(outputdir, "expected.png")
		difference_name = os.path.join(outputdir, "difference.png")

		imageA.save(actual_name)
		imageB.save(expected_name)
		difference.save(difference_name)

		# Replace the difference image with a message that test runners can
		# display.
		difference = (
				"Image differences found. Actual: %s Expected: %s "
				"Difference: %s" % (
					actual_name, expected_name, difference_name,
				)
			)

	return difference
