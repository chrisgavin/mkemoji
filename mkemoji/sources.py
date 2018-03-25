import abc
import pathlib
import typing

from wand.image import Image
import requests

class ImageSource(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def can_handle(self, source:str) -> bool: pass

	@abc.abstractmethod
	def get_image(self, source:str) -> Image: pass

	@staticmethod
	def has_scheme(scheme:str, source:str) -> bool:
		return source.split("://", 2)[0] == scheme

class LocalImageSource(ImageSource):
	def can_handle(self, source:str) -> bool:
		return not "://" in source and pathlib.Path(source).is_file()

	def get_image(self, source:str) -> Image:
		return Image(filename=source)

class WebImageSource(ImageSource):
	def can_handle(self, source:str) -> bool:
		return self.has_scheme("http", source) or self.has_scheme("https", source)

	def get_image(self, source:str) -> Image:
		response = requests.get(source)
		response.raise_for_status()
		return Image(blob=response.content)

def concrete_sources(base_class:typing.Type[ImageSource]=ImageSource) -> typing.List[ImageSource]:
	sources = [] # type: typing.List[ImageSource]
	for subclass in base_class.__subclasses__():
		if not subclass.__abstractmethods__: # type: ignore
			sources += [subclass()]
		sources += concrete_sources(subclass)
	return sources

def get_source(image:str) -> ImageSource:
	matching_source = None
	for source in concrete_sources():
		if source.can_handle(image):
			if matching_source is not None:
				raise SystemExit("Two sources claimed to be able to handle \"%s\". Please raise a bug report for mkemoji." % image)
			matching_source = source
	if matching_source is None:
		raise SystemExit("mkemoji doesn't know what to do with \"%s\". It should either be a local image file, or a URL of an image." % image)
	return matching_source

def get_image(image:str) -> Image:
	return get_source(image).get_image(image)
