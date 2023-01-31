from sprite_object import SpriteObject
from utils import distance
from settings import SETTINGS

import pygame
from pygame.math import Vector2
from random import uniform, randint


class Fireball(SpriteObject):
	def __init__(
			self,
			game,
			path: str = 'assets/sprites/fireball.png',
			pos: tuple = (10.5, 4.5),
			scale: float = 0.25,
			shift: int = 0.5,
			direction: Vector2 = None,
			noclip: bool = False
	):
		"""
		Creates a fireball.
		:param direction: The direction of the fireball. A 2D vector. Set randomly if None. None by default.
		:param noclip: Whether the fireball clips through walls. False by default.
		"""
		super().__init__(game, path, pos, scale, shift)
		# Lowers the culling distance a ton so the player can still see the fireball even if really close by
		self.culling_distance = 0.1

		# Remembers the direction of the projectile
		self.direction = direction
		if self.direction is None:
			self.direction = Vector2(uniform(-1, 1), uniform(-1, 1)) / randint(200, 400)

		# Remembers whether it clips through walls.
		self.noclip = noclip
		if self.noclip:
			self.image = pygame.image.load('assets/sprites/fireball_blue.png').convert_alpha()


	def check_wall(self, x:int, y:int) -> bool:
		"""
		Checks whether given coordinates are intersecting with a wall within the world map.
		"""
		return (x, y) not in self.game.map.world_map


	def update(self):
		"""
		Called every frame : If the player is colliding with the projectile, we lower their health.
		"""
		super().update()

		# Moves the projectile towards the given direction
		if self.noclip:
			self.x += self.direction.x * self.game.delta_time
			self.y += self.direction.y * self.game.delta_time
		else:
			previous_pos = (self.x, self.y)
			if self.check_wall(int(self.x + self.direction.x * self.SPRITE_SCALE), int(self.y)):
				self.x += self.direction.x * self.game.delta_time
			if self.check_wall(int(self.x), int(self.y + self.direction.y * self.SPRITE_SCALE)):
				self.y += self.direction.y * self.game.delta_time

			# Destroys the projectile if it collided with a wall
			if (self.x, self.y) == previous_pos:
				self.destroy()


		# Finds the distance between the projectile and the player
		if distance(self.game.player.x, self.x, self.game.player.y, self.y) < SETTINGS.player.player_size_scale / 100:
			# Lowers the player health
			self.game.player.health -= 1
			self.game.player.check_health()
			# Removes the projectile from the list of sprites
			self.destroy()

		# If the projectile is out of bounds, destroys it
		if self.x < 0 or self.x > self.game.map.map_size[0] or self.y < 0 or self.y > self.game.map.map_size[1]:
			self.destroy()


	def destroy(self):
		"""
		Destroys the projectile.
		"""
		self.game.objects_handler.sprites_list.remove(self)
