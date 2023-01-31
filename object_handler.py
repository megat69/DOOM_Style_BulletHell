import pygame
from random import uniform

from sprite_object import SpriteObject, AnimatedSprite
from fireball import Fireball
from entity import Entity


class ObjectHandler:
	"""
	Handles all objects in the game.
	"""
	def __init__(self, game):
		self.game = game
		self.sprites_list = []
		self.entities = []
		self.entity_positions = set()
		self.entity_sprite_path = 'assets/entities/'
		self.static_sprites_path = 'assets/sprites/'
		self.animated_sprites_path = "assets/animated_sprites/"

		# Sprite creation
		self.add_sprite(SpriteObject(game))
		self.add_sprite(AnimatedSprite(game))
		self.add_sprite(Fireball(game, direction=pygame.math.Vector2(0, 0)))
		for _ in range(10):
			self.create_enemy()

	def update(self):
		"""
		Updates all sprites and entities in the game.
		"""
		self.entity_positions = {entity.map_pos for entity in self.entities if entity.alive}
		[sprite.update() for sprite in self.sprites_list]
		[entity.update() for entity in self.entities]

	def add_sprite(self, sprite: SpriteObject):
		"""
		Adds a sprite to the handler.
		:param sprite: The sprite to add.
		"""
		self.sprites_list.append(sprite)


	def add_entity(self, entity: Entity):
		"""
		Adds an entity to the handler.
		:param entity: The entity to add.
		"""
		self.entities.append(entity)


	def create_enemy(self):
		"""
		Adds an enemy to the map.
		"""
		self.add_entity(
			Entity(self.game, pos=(uniform(1, self.game.map.map_size[0] - 1), uniform(1, self.game.map.map_size[1] - 1))))
		while self.entities[-1].check_wall(self.entities[-1].x, self.entities[-1].y) is False:
			self.entities[-1].x = uniform(1, self.game.map.map_size[0] - 1)
			self.entities[-1].y = uniform(1, self.game.map.map_size[0] - 1)
