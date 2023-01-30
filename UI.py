import pygame
pygame.font.init()
from typing import Callable, Tuple


class UI:
	def __init__(self, game):
		"""
		Creates the UI.
		"""
		self.game = game
		self.UI_elements = {}


	def create_UI_element(self, name: str, text: str, font_name: str, font_size: int, update: Callable,
	                      position: Tuple[int, int], color: Tuple[int, int, int] = (0, 0, 0)):
		"""
		Creates a new UI element.
		"""
		self.UI_elements[name] = {
			"text": text,
			"font": pygame.font.SysFont(font_name, font_size),
			"update": update,
			"position": position,
			"color": color
		}

	def update(self):
		"""
		Updates each UI element.
		"""
		for element in self.UI_elements.values():
			element["update"](self.game, element)


	def draw(self):
		for element in self.UI_elements.values():
			text_surface = element["font"].render(element["text"], False, element["color"])
			self.game.screen.blit(text_surface, element["position"])
