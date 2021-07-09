import abc
import typing

from wand.image import Image
import requests
import slacktoken.token

class ImageSink(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def max_resolution(self) -> int: pass

	@abc.abstractmethod
	def add_emoji(self, name:str, emoji: Image, replace:bool) -> None: pass

class SlackImageSink(ImageSink):
	def max_resolution(self) -> int:
		return 128

	def add_emoji(self, name:str, emoji: Image, replace:bool) -> None:
		team, name = self.parse_name(name)
		authentication_information = slacktoken.token.get(team)
		session = requests.session()
		for key, value in authentication_information.cookies.items():
			session.cookies.set(key, value)
		if replace:
			response = session.post(
				"https://%s.slack.com/api/emoji.remove" % team,
				data={
					"token": authentication_information.token,
					"name": name,
				},
			)
			response.raise_for_status()
		response = session.post(
			f"https://{team}.slack.com/api/emoji.add",
			data={
				"token": authentication_information.token,
				"name": name,
				"mode": "data",
			},
			files={
				"image": emoji.make_blob(),
			},
		)
		response.raise_for_status()
		if "error" in response.json():
			raise SystemExit("Slack error: %s" % self.localize_error(response.json()["error"], replace))

	@staticmethod
	def parse_name(name:str) -> typing.Tuple[typing.Optional[str], str]:
		name_split = name.split("/", 2)
		if len(name_split) == 1:
			return (None, name_split[0])
		return (name_split[0], name_split[1])

	@staticmethod
	def localize_error(error:str, replace:bool) -> str:
		english = {
			"error_name_taken": "You don't have permission to remove the existing emoji." if replace else "An emoji with the requested name already exists.",
		}
		return english.get(error, error)
