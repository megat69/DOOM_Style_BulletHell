import pygame
from pygame.math import Vector2
import math

from settings import SETTINGS


class Player:
	"""
	The Player of the game.
	"""
	def __init__(self, game):
		"""
		Controls the player.
		:param game: An instance of the Game.
		"""
		self.game = game

		# Keeping in mind the player coords
		self.x, self.y = SETTINGS.player.pos
		self.angle = SETTINGS.player.angle


	def movement(self):
		"""
		Makes the player move
		"""
		# Determines the vector the player should follow to move forward
		sin_a = math.sin(self.angle)
		cos_a = math.cos(self.angle)

		# The player's direction vector
		direction = Vector2(0)

		# Calculating the player's speed based on its default speed and the delta time
		speed = SETTINGS.player.speed * self.game.delta_time

		# Precalculating the values of sine and cosine of the speed and angle
		speed_sin = speed * sin_a
		speed_cos = speed * cos_a

		# Gets the keys currently pressed
		keys = pygame.key.get_pressed()
		if keys[getattr(pygame, f"K_{SETTINGS.controls.forward}")]:
			direction.x += speed_cos
			direction.y += speed_sin
		if keys[getattr(pygame, f"K_{SETTINGS.controls.backward}")]:
			direction.x -= speed_cos
			direction.y -= speed_sin
		if keys[getattr(pygame, f"K_{SETTINGS.controls.left}")]:
			direction.x += speed_sin
			direction.y -= speed_cos
		if keys[getattr(pygame, f"K_{SETTINGS.controls.right}")]:
			direction.x -= speed_sin
			direction.y += speed_cos

		# Uses the calculated information to make the player move
		self.check_wall_collisions(direction)

		# Makes the player rotate
		if self.game.is_3D is False:
			if keys[pygame.K_LEFT]:
				self.angle -= SETTINGS.player.rotation_speed * self.game.delta_time
			if keys[pygame.K_RIGHT]:
				self.angle += SETTINGS.player.rotation_speed * self.game.delta_time
		self.angle %= math.tau


	def check_wall(self, x:int, y:int) -> bool:
		"""
		Checks whether given coordinates are intersecting with a wall within the world map.
		"""
		return (x, y) not in self.game.map.world_map


	def check_wall_collisions(self, direction:Vector2):
		"""
		Checks if the player is intersecting with a wall.
		"""
		if self.check_wall(int(self.x + direction.x), int(self.y)):
			self.x += direction.x
		if self.check_wall(int(self.x), int(self.y + direction.y)):
			self.y += direction.y


	def draw(self):
		"""
		Draws the player on the map.
		"""
		if self.game.is_3D is False:
			"""pygame.draw.line(
				self.game.screen,
				'yellow',
				(self.x * 100, self.y * 100),
				(
						self.x * 100 + SETTINGS.graphics.resolution[0] * math.cos(self.angle),
						self.y * 100 + SETTINGS.graphics.resolution[1] * math.sin(self.angle)
				),
				2
			)"""
			pygame.draw.circle(
				self.game.screen,
				'green',
				(self.x * 100, self.y * 100),
				15
			)

	def update(self):
		"""
		Runs every frame to determine the player's logic.
		"""
		# Makes the player move correctly
		self.movement()


	@property
	def pos(self):
		""" Returns the player's position """
		return self.x, self.y


	@property
	def map_pos(self):
		""" Returns the position of the tile the player is currently standing on """
		return int(self.x), int(self.y)