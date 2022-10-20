import pygame

from settings import SETTINGS

# Creates the map
map_size = tuple(map(lambda x: x // 100, SETTINGS.graphics.resolution))  # Best if corresponding to the window's aspect ratio
game_map = [
	[1 if row in (0, map_size[1] - 1) or column in (0, map_size[0] - 1) else False for column in range(map_size[0])] \
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
			[pygame.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
			 for pos in self.world_map]
