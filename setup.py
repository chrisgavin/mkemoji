#!/usr/bin/env python3
import sys
from setuptools import setup

def main(): # type: () -> None
	if sys.version_info[:2] < (3, 5):
		raise SystemExit("mkemoji requires at least Python 3.5.")
	setup(
		name="mkemoji",
		version="1.0.0",
		description="A script for turning images into Slack custom emoji.",
		url="https://gitlab.com/chrisgavin/mkemoji/",
		packages=["mkemoji"],
		python_requires=">=3.5",
		classifiers=[
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: 3 :: Only",
		],
		install_requires=[
			"lxml",
			"requests",
			"Wand",
		],
		extras_require={
			"tests": [
				"pytest",
				"pytest-mypy",
			],
		},
		entry_points={
			"console_scripts": [
				"mkemoji = mkemoji.__main__:main",
			],
		},
	)

if __name__ == "__main__":
	main()
