import pygame
from pygame.math import Vector2
import math

from settings import SETTINGS


class SpriteObject:
	def __init__(self, game, path='assets/sprites/candlebra.png', pos=(10.5, 3.5)):
		"""
		Creates a new sprite instance.
		:param game: The Game instance.
		:param path: The path to the sprite texture.
		:param pos: The psoition of the sprite in the level.
		"""
		self.game = game
		self.player = game.player  # Creating a shorthand
		self.x, self.y = pos
		self.image = pygame.image.load(path).convert_alpha()
		self.IMAGE_WIDTH = self.image.get_width()
		self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
		self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
		# Initialization of later attributes
		self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 1, 1
		self.sprite_half_width = 0


	def get_sprite(self):
		"""
		Gets the sprite correctly placed in 3D space.
		"""
		# Calculating the angle in which the player will face the sprite (theta angle)
		direction = Vector2(self.x - self.player.x, self.y - self.player.y)
		self.dx, self.dy = direction
		self.theta = math.atan2(direction.y, direction.x)

		# Looks for the delta angle
		delta = self.theta - self.player.angle
		if (direction.x > 0 and self.player.angle > math.pi) or (direction.x < 0 and direction.y < 0):
			delta += math.tau

		# We calculate how many rays are in the delta angle
		delta_rays = delta / SETTINGS.graphics.delta_angle

		# Calculates the Sprite's position based on the last math
		self.screen_x = (SETTINGS.graphics.half_num_rays + delta_rays) * SETTINGS.graphics.scale

		# Calculates the Sprite's size
		self.dist = math.hypot(direction.x, direction.y)
		self.norm_dist = self.dist * math.cos(delta)

		# Only makes further calculations if the sprite is in the visible spectrum
		if -self.IMAGE_HALF_WIDTH < self.screen_x < (SETTINGS.graphics.resolution[0] + self.IMAGE_HALF_WIDTH) and\
				self.norm_dist > 0.5:
			self.get_sprite_projection()


	def get_sprite_projection(self):
		"""
		Gets the projected image of the sprite.
		"""
		proj = SETTINGS.graphics.screen_distance / self.norm_dist
		# Takes into account different image ratios
		proj_width, proj_height = proj * self.IMAGE_RATIO, proj

		# Scales the sprite to the calculated size
		image = pygame.transform.scale(self.image, (proj_width, proj_height))

		# Finds the sprite's position on the screen
		self.sprite_half_width = proj_width // 2
		pos = self.screen_x - self.sprite_half_width, SETTINGS.graphics.resolution[1] // 2 - proj_height // 2

		# Adds the sprite to the array of objects to render during raycasting
		self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))


	def update(self):
		"""
		Updates the sprite every frame.
		"""
		self.get_sprite()