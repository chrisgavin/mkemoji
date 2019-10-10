import abc
import json
import pathlib
import re
import sqlite3
import typing

from wand.image import Image
import requests

class ImageSink(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def max_resolution(self) -> int: pass

	@abc.abstractmethod
	def add_emoji(self, name:str, emoji: Image) -> None: pass

class SlackImageSink(ImageSink):
	def max_resolution(self) -> int:
		return 128

	def add_emoji(self, name:str, emoji: Image) -> None:
		cookies = self.get_slack_cookies()
		teams = self.get_slack_teams()
		team, name = self.parse_name(name)
		if team is None:
			if len(teams) == 1:
				team = teams[0]
			else:
				raise SystemExit("You are signed in to multiple Slack teams, so the emoji name should be prefixed with a team name. e.g. (%s/%s)" % (teams[0], name))
		else:
			if team not in teams:
				raise SystemExit("You don't seem to be signed in to the \"%s\" Slack team." % team)
		response = requests.get("https://%s.slack.com/" % team, cookies=cookies)
		matcher = re.search("\"api_token\":\"([^\"]+)\"", response.text)
		if matcher is None:
			raise SystemExit("Could not find Slack token. Maybe the Slack webpage has changed.")
		token = matcher.group(1)
		response = requests.post(
			"https://%s.slack.com/api/emoji.add" % team,
			data={
				"token": token,
				"name": name,
				"mode": "data",
			},
			files={
				"image": emoji.make_blob(),
			},
		)
		response.raise_for_status()
		if "error" not in response.json():
			return
		raise SystemExit("Slack error: %s" % self.localize_error(response.json()["error"]))

	@staticmethod
	def parse_name(name:str) -> typing.Tuple[typing.Optional[str], str]:
		name_split = name.split("/", 2)
		if len(name_split) == 1:
			return (None, name_split[0])
		return (name_split[0], name_split[1])

	@staticmethod
	def get_slack_cookies() -> typing.Dict[str, str]:
		cookie_database_path = pathlib.Path.home() / ".config" / "Slack" / "Cookies"
		if not cookie_database_path.is_file():
			raise SystemExit("Could not find Slack cookie database. Is Slack installed and have you logged in?")
		cookie_database = sqlite3.connect(str(cookie_database_path))
		cookie_cursor = cookie_database.cursor()
		cookie_cursor.execute("SELECT value FROM cookies WHERE host_key=\".slack.com\" AND name=\"d\"")
		cookie = cookie_cursor.fetchone()
		if cookie is None:
			raise SystemExit("Could not find login cookie in Slack cookie database. Is have you logged in to Slack?")
		return {"d": cookie[0]}

	@staticmethod
	def get_slack_teams() -> typing.List[str]:
		teams_path = pathlib.Path.home() / ".config" / "Slack" / "storage" / "slack-workspaces"
		if not teams_path.is_file():
			raise SystemExit("Could not find Slack teams file. Is Slack installed and have you signed in to a team?")
		with teams_path.open() as teams_file:
			teams = json.load(teams_file)
		return [team["domain"] for team in teams.values()]

	@staticmethod
	def localize_error(error:str):
		english = {
			"error_name_taken": "An emoji with the requested name already exists.",
		}
		return english.get(error, error)
