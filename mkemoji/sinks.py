import abc
import json
from lxml import html
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
		target = "https://%s.slack.com/customize/emoji" % team
		response = requests.get(target, cookies=cookies)
		matcher = re.search("<input type=\"hidden\" name=\"crumb\" value=\"([^\"]+)\"", response.text)
		if matcher is None:
			raise SystemExit("Could not find Slack crumb. Maybe the Slack webpage has changed.")
		crumb = matcher.group(1)
		response = requests.post(
			target,
			data={
				"add": "1",
				"crumb": crumb,
				"name": name,
				"mode": "data",
				"aliased": "",
				"resized": "",
			},
			files={
				"img": emoji.make_blob(),
			},
			cookies=cookies,
		)
		response.raise_for_status()
		if response.url.endswith("?added=1&name=" + name):
			return
		content = html.fromstring(response.content)
		error = content.xpath("//p[contains(concat(' ', @class, ' '), ' alert_error ')]")
		if error:
			html_error = html.tostring(error[0])
			text_error = re.sub("<.*?>", "", html_error.decode("utf-8"))
			text_error = text_error.strip()
			raise SystemExit("Slack error: %s" % text_error)
		else:
			raise SystemExit("Unknown Slack error.")

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
		teams_path = pathlib.Path.home() / ".config" / "Slack" / "storage" / "slack-teams"
		if not teams_path.is_file():
			raise SystemExit("Could not find Slack teams file. Is Slack installed and have you signed in to a team?")
		with teams_path.open() as teams_file:
			teams = json.load(teams_file)
		team_urls = [team["team_url"] for team in teams.values() if team["hasValidSession"]]
		if not team_urls:
			raise SystemExit("Could not find any Slack teams. Have you signed in to a team?")
		team_names = [] # type: typing.List[str]
		for team_url in team_urls:
			matcher = re.match("^https://([^\\.]+)\\.slack\\.com/.*$", team_url)
			if matcher is None:
				raise SystemExit("Team URL \"%s\" was not in an expected format." % team_url)
			team_names += [matcher.group(1)]
		return team_names