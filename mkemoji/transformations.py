from wand.image import Image

def transform(image:Image, max_resolution:int) -> Image:
	image.trim()

	resize_geometry = "%dx%d>" % (max_resolution, max_resolution)
	image.transform(resize=resize_geometry)

	return image
