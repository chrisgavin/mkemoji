#!/usr/bin/env python3
import argparse

from mkemoji import sources, transformations, sinks

def main() -> None:
	parser = argparse.ArgumentParser(description="Turn any image into a Slack emoji from the command line.")
	parser.add_argument("image", help="A path to or URL of an image to be turned into an emoji.")
	parser.add_argument("name", help="The name of the emoji. Prefix with \"team-name/\" if you are signed into multiple teams.")
	parser.add_argument("--replace", action="store_true", help="Replace an existing emoji.")
	args = parser.parse_args()

	with sources.get_image(args.image) as image:
		sink = sinks.SlackImageSink()
		image = transformations.transform(image, sink.max_resolution())
		sink.add_emoji(args.name, image, args.replace)

if __name__ == "__main__":
	main()
