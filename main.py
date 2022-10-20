import pygame
import sys

from settings import SETTINGS
from map import Map
from player import Player
from raycasting import RayCasting


class Game:
	"""
	The main game instance.
	"""
	def __init__(self):
		# Initializes pygame
		pygame.init()

		# Creates the main application's window
		self.screen = pygame.display.set_mode(SETTINGS.graphics.resolution)

		# The game's clock system (keeps a constant framerate and delta time)
		self.delta_time = 1
		self.clock = pygame.time.Clock()

		# Creates a new game.
		self.new_game()


	def new_game(self):
		"""
		Creates a new game.
		"""
		# Loads the game's map
		self.map = Map(self)

		# Loads the player
		self.player = Player(self)

		# Loads the pseudo3D engine
		self.raycasting = RayCasting(self)

		# Starts in 2D
		self.is_3D = False


	def update(self):
		"""
		Runs every frame, contains the game's main logic.
		"""
		# Updates the player position
		self.player.update()

		# Updates the engine
		self.raycasting.update()

		# Erases the pygame display
		pygame.display.flip()

		# Waits until a new frame has to be drawn and calculates the delta time
		self.delta_time = self.clock.tick(SETTINGS.graphics.framerate)

		# Displays the game's title with the framerate in the caption
		pygame.display.set_caption(f"DOOM Style Bullet Hell - {self.clock.get_fps():.1f} FPS")


	def draw(self):
		"""
		Gets called every frame to draw the main sprites to the screen.
		"""
		# Fills the screen with black
		self.screen.fill((0, 0, 0))

		if self.is_3D is False:
			# Draws the map
			self.map.draw()

			# Draws the player
			self.player.draw()


	def check_events(self):
		"""
		Checks for events having occurred during the frame.
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit(0)

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.is_3D = not self.is_3D


	def run(self):
		"""
		Runs the game, and starts the game's main loop, running each of its components for as long as necessary.
		"""
		while True:
			# Checks for all game events having occured within the frame
			self.check_events()

			# We update the game's logic
			self.update()

			# We draw all sprites
			self.draw()


if __name__ == "__main__":
	# Instantiates the Game and runs it
	game = Game()
	game.run()
