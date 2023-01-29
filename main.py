import pygame
import sys
import math

from settings import SETTINGS
from map import Map
from player import Player
from raycasting import RayCasting
from object_renderer import ObjectRenderer
from object_handler import ObjectHandler
from weapon import Shotgun, Pistol
from sounds import SoundHandler

# TODO : Muzzle flashes
# TODO : Normalize player movement direction
# TODO : Enemies
# TODO : Fireballs
# TODO : First map
class Game:
	"""
	The main game instance.
	"""
	def __init__(self):
		# Initializes pygame
		pygame.init()

		# Creates the main application's window
		self.screen = pygame.display.set_mode(SETTINGS.graphics.resolution)
		self.rendering_surface = pygame.Surface(SETTINGS.graphics.resolution)

		# The game's clock system (keeps a constant framerate and delta time)
		self.delta_time = 1
		self.clock = pygame.time.Clock()

		# Creates a new game.
		self.new_game()


	def new_game(self):
		"""
		Creates a new game.
		"""
		# Loads all the sounds
		self.sound = SoundHandler(self)

		# Loads the game's map
		self.map = Map(self)

		# Loads the player
		self.player = Player(self)

		# Loads the object renderer
		self.object_renderer = ObjectRenderer(self)

		# Loads the pseudo3D engine
		self.raycasting = RayCasting(self)

		# Loads the objects handler
		self.objects_handler = ObjectHandler(self)

		# Loads the weapon
		self.weapons = [Shotgun(self), Pistol(self)]
		self.current_weapon = 0
		self.weapon = self.weapons[self.current_weapon]

		# Starts in 2D
		self.is_3D: bool = False


	def update(self):
		"""
		Runs every frame, contains the game's main logic.
		"""
		# Updates the player position
		self.player.update()

		# Updates the engine
		self.raycasting.update()

		# Updates the objects in the game
		self.objects_handler.update()

		# Updates the weapon
		self.weapon = self.weapons[self.current_weapon]
		self.weapon.update()

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
		# If we play in 2D, we render the player and the map
		if self.is_3D is False:
			# Fills the screen with the floor color if in 2D
			self.screen.fill(SETTINGS.graphics.floor_color)

			# Draws the map
			self.map.draw()

			# Draws the player
			self.player.draw()

		# If playing in 3D, we render the project mapping
		else:
			# Renders all the objects on the rendering surface
			self.object_renderer.draw()

			# We calculate the view bobbing based on the elapsed time, the strength, and whether the player is moving
			view_bobbing = math.sin(pygame.time.get_ticks() / 300) * 5 * SETTINGS.graphics.view_bobbing_strength * (
					1 + self.player.is_moving
			) + (2 * self.weapon.reloading)

			# We blit the rendering surface onto the screen
			self.screen.blit(self.rendering_surface, (0, view_bobbing * SETTINGS.graphics.view_bobbing))

			# Draws the weapon
			self.weapon.draw()


	def check_events(self):
		"""
		Checks for events having occurred during the frame.
		"""
		for event in pygame.event.get():
			# Monitors the leave event (press of escape key or window closing)
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit(0)

			if event.type == pygame.KEYDOWN:
				# Monitors the perspective change
				if event.key == getattr(pygame, f"K_{SETTINGS.controls.perspective_change.upper()}"):
					# Toggles 3D mode
					self.is_3D = not self.is_3D

					# Hides the mouse if in 3D mode
					pygame.mouse.set_visible(not pygame.mouse.get_visible())
					pygame.event.set_grab(not pygame.event.get_grab())

			# Switches weapons based on mouse wheel
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4:
					self.current_weapon -= 1
					if self.current_weapon < 0:
						self.current_weapon = len(self.weapons) - 1
				elif event.button == 5:
					self.current_weapon += 1
					if self.current_weapon >= len(self.weapons):
						self.current_weapon = 0

			# Allows the player to take a shot
			if self.is_3D:
				self.player.single_fire_event(event)


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
