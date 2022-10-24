import pygame
import os

from settings import SETTINGS


class ObjectRenderer:
	"""
	Renders all objects in the game.
	"""
	def __init__(self, game):
		"""
		:param game: The instance of the Game.
		"""
		self.game = game
		self.screen = self.game.screen
		self.wall_textures = self.load_wall_textures()


	def draw(self):
		"""
		Draws the game objects' render.
		"""
		self.render_game_objects()


	def render_game_objects(self):
		"""
		Renders all objects in the game.
		"""
		objects_list = self.game.raycasting.objects_to_render

		# Fetches all objects in the raycast results and renders them
		for depth, image, pos in objects_list:
			self.screen.blit(image, pos)


	@staticmethod
	def get_texture(path:str, resolution:tuple=(SETTINGS.graphics.texture_size, SETTINGS.graphics.texture_size)):
		"""
		Loads the texture from the specified path and returns a scaled image.
		:param path: The path to the texture.
		:param resolution: The texture resolution, default is defined in settings.json
		:return: The loaded and scaled texture.
		"""
		texture = pygame.image.load(path).convert_alpha()
		return pygame.transform.scale(texture, resolution)


	def load_wall_textures(self):
		"""
		Loads all the wall textures.
		"""
		return {
			i: self.get_texture(f"assets/textures/{i}.png")
			for i in range(1, len(os.listdir(os.path.join(os.path.dirname(__file__), "assets/textures/"))) + 1)
		}
