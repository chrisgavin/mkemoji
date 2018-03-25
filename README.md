# mkemoji
A script for turning images into Slack custom emoji.

## Installation
```
pip3 install mkemoji
```

## Usage
```
mkemoji "https://raw.githubusercontent.com/googlei18n/noto-emoji/master/png/128/emoji_u26c4.png" my-slack-team/noto-snowman
```

The tool will automatically authenticate to Slack using the cookies from your local Slack client.

## Features
* Automatically trims borders from images so that they appear the maximum possible size in Slack.
* Downscales images to meet Slack's resolution requirements.
