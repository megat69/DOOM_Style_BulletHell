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

		# Creates a depth texture, storing the depth of everything on the screen in one texture
		self.depth_texture = pygame.Surface(SETTINGS.graphics.resolution).convert()

		# Creates a texture for the ambient occlusion
		self.ambient_occlusion_texture = pygame.Surface(SETTINGS.graphics.resolution).convert()


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
			self.sky_offset = (self.sky_offset + 0.75 * self.game.player.rel) % SETTINGS.graphics.resolution[0]

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

		# Clears the depth texture
		# self.depth_texture.fill((0, 0, 0))

		# Normalize function
		normalize_depth = lambda x: (1 - (x / SETTINGS.graphics.max_depth)) * 255


		# Fetches all objects in the raycast results and renders them
		for depth, image, pos in objects_list:
			# Draws the wall fragment to the wall
			self.screen.blit(image, pos)

			# Drawing to the depth texture
			"""normalized_depth = normalize_depth(depth)
			try:
				pygame.draw.rect(
					self.depth_texture,
					(normalized_depth, normalized_depth, normalized_depth),
					pygame.Rect(
						pos[0], pos[1],
						image.get_width(), image.get_height()
					)
				)
			except ValueError: pass"""



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
