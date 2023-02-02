import pygame
from random import randint
import json

from settings import SETTINGS
from sprites import ALL_SPRITES

# -- Creates the map --
# Generates the map's size based on the resolution, best if corresponding to the window's aspect ratio
# map_size = tuple(map(lambda x: x // 64, SETTINGS.graphics.resolution))
# Generates the map with its boundaries
# game_map = [
# 	[(1 + (1 if randint(0, 5) == 0 or not (row in (0, map_size[1] - 1) or column in (0, map_size[0] - 1)) else 0)) if row in (0, map_size[1] - 1) or column in (0, map_size[0] - 1) or randint(0, 5) == 5 else False for column in range(map_size[0])]
# 	# [1 if row in (0, map_size[1] - 1) or column in (0, map_size[0] - 1) else 0 for column in range(map_size[0])]
# 	for row in range(map_size[1])
# ]


class Map:
	"""
	The class containing the game's map system.
	"""
	def __init__(self, game):
		"""
		Initializes the class using the Game class.
		:param game: The instance of the Game.
		"""
		self.game = game

		# Loads the map from json
		with open("maps/map0.json", "r") as map_data_file:
			map_data = json.load(map_data_file)

		self.map = map_data["map"]
		self.tile_size = map_data["tile_size"]
		self.map_size = tuple(map(lambda x: x // self.tile_size, SETTINGS.graphics.resolution))
		self.world_map = {}
		self.get_map()
		self.map_title = map_data["map_title"]
		self.base_enemy_spawn = map_data["base_enemy_spawn"]  # Base amount of enemies on the map
		self.max_enemies = map_data["max_enemies"]  # Max amount of enemies on the map
		self.map_data = map_data

	def load_sprites(self):
		"""
		Loads the sprites.
		"""
		for sprite in self.map_data["sprites"]:
			self.game.objects_handler.add_sprite(
				ALL_SPRITES[sprite["name"]](
					self.game,
					pos=sprite["pos"]
				)
			)

	def get_map(self):
		"""
		Writes the map to the world map.
		"""
		for j, row in enumerate(self.map):
			for i, value in enumerate(row):
				if value:
					self.world_map[(i, j)] = value


	def draw(self):
		"""
		Draws the 2D map on the screen.
		"""
		if self.game.is_3D is False:
			for pos, value in self.world_map.items():
				self.game.screen.blit(
					pygame.transform.scale(self.game.object_renderer.wall_textures[value], (self.tile_size, self.tile_size)),
					(pos[0] * self.tile_size, pos[1] * self.tile_size)
				)
