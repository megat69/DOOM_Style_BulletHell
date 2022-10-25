import pygame

from settings import SETTINGS
from sprite_object import AnimatedSprite


class Entity(AnimatedSprite):
	def __init__(
			self,
			game,
			path: str = 'assets/entities/soldier/0.png',
			pos: tuple = (11.5, 5.5),
			scale: float = 0.6,
			shift: int = 0.38,
			animation_time: int = 180
	):
		super().__init__(game, path, pos, scale, shift, animation_time)
		# Loads all images for each state
		self.images = {
			'attack': self.get_images(self.path + '/attack'),
			'death': self.get_images(self.path + '/death'),
			'idle': self.get_images(self.path + '/idle'),
			'pain': self.get_images(self.path + '/pain'),
			'walk': self.get_images(self.path + '/walk'),
		}

		# Entity parameters
		self.attack_distance = 20
		self.speed = 0.035
		self.size = 10
		self.health = 100
		self.alive = True
		self.in_pain = True

	def update(self):
		"""
		Updates the logic of the entity.
		"""
		self.check_animation_time()
		super().update()