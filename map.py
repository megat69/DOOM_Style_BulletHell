import pygame
import time
import os
import json
from importlib import import_module

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
	TITLE_SCREEN_DURATION   = 2
	TITLE_SCREEN_BLEND_TIME = 3
	def __init__(self, game):
		"""
		Initializes the class using the Game class.
		:param game: The instance of the Game.
		"""
		self.game = game

		# Loads the map from json
		try:
			with open(f"maps/map{game.save_data['current_level']}.json", "r") as map_data_file:
				map_data = json.load(map_data_file)
		except FileNotFoundError:  # If the level doesn't exist
			with open(os.path.join(SETTINGS.misc.save_location, "save_data.json"), "w") as save_data_file:
				print("Level was reset !")
				self.game.save_data['current_level'] = 0
				json.dump(self.game.save_data, save_data_file, indent=2)
			with open(f"maps/map{game.save_data['current_level']}.json", "r") as map_data_file:
				map_data = json.load(map_data_file)

		# Loads the map code
		self.map_code = import_module(f"maps.map{game.save_data['current_level']}")

		self.map = map_data["map"]
		self.tile_size = map_data["tile_size"]
		self.map_size = tuple(map(lambda x: x // self.tile_size, SETTINGS.graphics.resolution))
		self.world_map = {}
		self.get_map()
		self.map_title = map_data["map_title"]
		self.base_enemy_spawn = map_data["base_enemy_spawn"]  # Base amount of enemies on the map
		self.max_enemies = map_data["max_enemies"]  # Max amount of enemies on the map
		self.map_data = map_data
		self.sprites_awaiting_appearance = []

		# Uses the perspective the map wants us to start with
		self.game.is_3D = not self.map_data["starting_perspective_is_2D"]
		pygame.event.set_grab(self.game.is_3D)
		pygame.mouse.set_visible(not self.game.is_3D)


	def load_title_ui(self):
		"""
		Creates the title of the level
		"""
		def title_update(game, element):
			if element["position"][0] + 400 > 0:
				element["position"][0] -= game.delta_time / 15

		self.game.UI.create_UI_element(
			"level_title", self.map_data["map_title"], "Impact", 40, title_update,
			[100, SETTINGS.graphics.resolution[1] - 120], (255, 255, 255), force=True
		)

	def load_sprites(self):
		"""
		Loads the sprites.
		"""
		for sprite in self.map_data["sprites"]:
			if "appearance" not in sprite.keys():
				sprite_data = sprite.get("data")
				if sprite_data is None:
					sprite_data = {}
				self.game.objects_handler.add_sprite(
					ALL_SPRITES[sprite["name"]](
						self.game,
						pos=sprite["pos"],
						**sprite_data
					)
				)
			else:
				self.sprites_awaiting_appearance.append(sprite)


	def load_enemies(self):
		"""
		Loads all the enemies.
		"""
		pass


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


	def update(self):
		"""
		Updates every frame.
		"""
		# Runs the function to check if each sprite can appear
		for sprite in self.sprites_awaiting_appearance:
			if self.map_code.FUNCTIONS[sprite["appearance"]](self.game):
				self.game.objects_handler.add_sprite(
					ALL_SPRITES[sprite["name"]](
						self.game,
						pos=sprite["pos"]
					)
				)
				self.sprites_awaiting_appearance.remove(sprite)
