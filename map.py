import pygame
from random import randint

from settings import SETTINGS

# -- Creates the map --
# Generates the map's size based on the resolution, best if corresponding to the window's aspect ratio
map_size = tuple(map(lambda x: x // 100, SETTINGS.graphics.resolution))
# Generates the map with its boundaries
game_map = [
	[(1 + (1 if randint(0, 5) == 0 or not (row in (0, map_size[1] - 1) or column in (0, map_size[0] - 1)) else 0)) if row in (0, map_size[1] - 1) or column in (0, map_size[0] - 1) or randint(0, 5) == 5 else False for column in range(map_size[0])] \
	for row in range(map_size[1])
]


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
		self.map = game_map
		self.world_map = {}
		self.get_map()


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
					pygame.transform.scale(self.game.object_renderer.wall_textures[value], (100, 100)),
					(pos[0] * 100, pos[1] * 100)
				)
