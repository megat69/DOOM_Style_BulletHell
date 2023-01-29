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
		self.screen = self.game.rendering_surface
		self.wall_textures = self.load_wall_textures()
		IMAGE_RESOLUTION = (SETTINGS.graphics.resolution[0], SETTINGS.graphics.resolution [1] // 2)
		self.sky_texture = self.get_texture('assets/textures/sky.png', IMAGE_RESOLUTION)
		self.sky_offset = 0


	def draw(self):
		"""
		Draws the game objects' render.
		"""
		# Renders the sky
		self.draw_background()

		# Renders all the game objects
		self.render_game_objects()


	def draw_background(self):
		"""
		Draws the sky texture if in 3D.
		"""
		if self.game.is_3D:
			# Gets the offset of the sky texture
			self.sky_offset = (self.sky_offset + 2.0 * self.game.player.rel) % SETTINGS.graphics.resolution[0]

			# Draws two sky textures, each being slightly offset so it matches the perspective
			self.screen.blit(self.sky_texture, (-self.sky_offset, 0))
			self.screen.blit(self.sky_texture, (-self.sky_offset + SETTINGS.graphics.resolution[0], 0))

			# Draws the floor color
			pygame.draw.rect(
				self.screen,
				SETTINGS.graphics.floor_color,
				(
					0, SETTINGS.graphics.resolution[1] // 2,
					SETTINGS.graphics.resolution[0], SETTINGS.graphics.resolution[1],
				)
			)


	def render_game_objects(self):
		"""
		Renders all objects in the game.
		"""
		# Gets the list of objects to render, and sorts them by the first away to the closest
		objects_list = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)

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
			i: self.get_texture(f"assets/textures/walls/{i}.png")
			for i in range(1, len(os.listdir(os.path.join(os.path.dirname(__file__), "assets/textures/walls/"))) + 1)
		}
