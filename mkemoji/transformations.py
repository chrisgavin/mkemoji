from wand.image import Image

def transform(image:Image, max_resolution:int) -> Image:
	image.trim()

	width = image.width
	height = image.height
	scale_factor = max_resolution / max(width, height)
	scale_factor = min(1, scale_factor)

	width = int(width * scale_factor)
	height = int(height * scale_factor)
	image.resize(width, height)

	return image
