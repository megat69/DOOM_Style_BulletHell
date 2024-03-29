import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN, QUIT, MOUSEBUTTONDOWN, KEYDOWN
import sys
import math
from random import randint, uniform, choice
import time
import os
import json

from settings import SETTINGS
from map import Map
from player import Player
from raycasting import RayCasting
from object_renderer import ObjectRenderer
from object_handler import ObjectHandler
from weapon import Shotgun, Pistol, Fist, ALL_WEAPONS
from sounds import SoundHandler
from UI import UI
from entity import Entity
from fireball import Fireball

# TODO : Bulle sans spawn
# TODO : Contact attack if player too close too long
# TODO : Parallelise raycast ?
# TODO : First map
class Game:
	"""
	The main game instance.
	"""
	def __init__(self):
		# Initializes pygame
		pygame.init()

		# Creates the main application's window
		flags = DOUBLEBUF  # Sets the flag for the window
		if SETTINGS.graphics.fullscreen:
			flags = flags | FULLSCREEN
		self.screen = pygame.display.set_mode(SETTINGS.graphics.resolution, flags)
		self.rendering_surface = pygame.Surface(SETTINGS.graphics.resolution)

		# Only authorizes some events for optimization
		pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])

		# The game's clock system (keeps a constant framerate and delta time)
		self.delta_time = 1
		self.clock = pygame.time.Clock()

		# Creates a new game.
		self.new_game()


	def new_game(self):
		"""
		Creates a new game.
		"""
		self.await_restart = False

		# Loads the save data
		with open(os.path.join(SETTINGS.misc.save_location, "save_data.json")) as save_data_file:
			self.save_data = json.load(save_data_file)

		# Remembers the start time
		self.start_time = time.time()

		# Starts in 2D
		self.is_3D: bool = False
		pygame.mouse.set_visible(True)

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

		# Loads the sprites on the map
		self.map.load_sprites()
		self.map.load_enemies()

		# Loads the weapon
		self.weapons = [
			ALL_WEAPONS[weapon](self)
			for weapon in self.map.map_data["available_weapons"]
		]
		self.current_weapon = 0
		self.weapon = self.weapons[self.current_weapon]

		# Loads the UI
		self.UI = UI(self)
		def update_framerate_ui_element(game, ui_element):
			ui_element["text"] = str(round(game.clock.get_fps())) if SETTINGS.graphics.show_FPS else ""
		self.UI.create_UI_element(
			"framerate", "", "Impact", 20, update_framerate_ui_element,
			(10, 10),
			(0, 255, 0)
		)
		def update_ammo_ui_element(game, ui_element):
			ui_element["text"] = str(game.weapon.ammo)
		self.UI.create_UI_element(
			"ammo", "", "Impact", 30, update_ammo_ui_element,
			(10, SETTINGS.graphics.resolution[1] - 50),
			(255, 255, 0)
		)
		def update_killed_ui_element(game, ui_element):
			ui_element["text"] = str(Entity.killed_entities)
		self.UI.create_UI_element(
			"killed", "", "Impact", 30, update_killed_ui_element,
			(SETTINGS.graphics.resolution[0] -50, SETTINGS.graphics.resolution[1] - 50),
			(0, 128, 255)
		)
		def update_health_ui_element(game, ui_element):
			ui_element["text"] = str(self.player.health)
		self.UI.create_UI_element(
			"health", "", "Impact", 30, update_health_ui_element,
			(75, SETTINGS.graphics.resolution[1] - 50),
			(255, 128, 0)
		)
		self.UI.create_UI_element(
			"health_symbol", "❤", "segoeuisymbol", 30, lambda x, y: None,
			(105, SETTINGS.graphics.resolution[1] - 50),
			(255, 128, 0)
		)
		self.map.load_title_ui()


	def update(self):
		"""
		Runs every frame, contains the game's main logic.
		"""
		# If we need to restart
		if self.await_restart:
			self.new_game()

		if self.player.health > 0:
			# Updates the map
			self.map.update()

			# Updates the player position
			self.player.update()

			# Updates the engine
			self.raycasting.update()

			# Updates the objects in the game
			self.objects_handler.update()

			# Updates the weapon
			self.weapon = self.weapons[self.current_weapon]
			self.weapon.update()

			# Updates the UI
			self.UI.update()

			# Infinitely spawns enemies and fireballs cuz why not
			if randint(0, 100) == 0 and len(self.objects_handler.entities) < self.map.max_enemies:
				self.objects_handler.create_enemy(fleer=randint(1, 4) == 1)

			"""self.screen.blit(self.raycasting._masking_surface, (0, 0), None, pygame.BLEND_RGBA_MULT)
			self.raycasting._masking_surface.fill('black')"""

		else:
			self.player.rel = 0
			pygame.event.set_grab(False)

		# Erases the pygame display
		pygame.display.flip()

		# Waits until a new frame has to be drawn and calculates the delta time
		self.delta_time = self.clock.tick(SETTINGS.graphics.framerate)

		# Displays the game's title with the framerate in the caption
		pygame.display.set_caption(f"DOOM Style Bullet Hell - {self.clock.get_fps():.1f} FPS")


	def get_weapon_by_name(self, name: str):
		"""
		Returns the weapon with the given name, and raises a NameError if not found.
		"""
		for element in self.weapons:
			if element.name == name:
				return element

		raise NameError(f"Weapon '{name}' not found !")


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
			self.screen.blit(self.rendering_surface, (0, view_bobbing * (SETTINGS.graphics.view_bobbing or self.player.health < 1)))

			# Draws the weapon
			self.weapon.draw()

			# Methods to draw the depth texture and AO
			# self.screen.blit(self.object_renderer.depth_texture.convert(), (0, 0))
			# self.screen.blit(self.object_renderer.ambient_occlusion_texture.convert(), (0, 0))

		# Draws the UI
		self.UI.draw()

		# Displays the title screen
		time_since_load = time.time() - self.start_time
		if time_since_load < Map.TITLE_SCREEN_DURATION + Map.TITLE_SCREEN_BLEND_TIME:
			blocker = pygame.Surface(SETTINGS.graphics.resolution).convert_alpha()
			if time_since_load < Map.TITLE_SCREEN_DURATION:
				blocker.fill((0, 0, 0))
			else:
				time_since_load -= Map.TITLE_SCREEN_DURATION
				clamp = lambda x: max(0, min(x, 1))  # Makes sure the number is between 0 and 1
				blocker.fill((0, 0, 0, 255 * clamp(1 - time_since_load / Map.TITLE_SCREEN_DURATION)))
			self.screen.blit(blocker, (0, 0))

		# Draws the UI
		self.UI.draw(True)


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
				if self.player.health < 1:
					self.new_game()
					return

				# Monitors the perspective change
				if event.key == getattr(pygame, f"K_{SETTINGS.controls.perspective_change.upper()}"):
					# Toggles 3D mode
					self.is_3D = not self.is_3D

					# Hides the mouse if in 3D mode
					pygame.mouse.set_visible(not pygame.mouse.get_visible())
					pygame.event.set_grab(self.is_3D)

				# Weapon change
				elif event.key in SETTINGS.controls.number_keys:
					event.key -= SETTINGS.controls.number_keys[0]
					if event.key < len(self.weapons):
						self.current_weapon = event.key

				# Melee
				elif event.key == getattr(pygame, f"K_{SETTINGS.controls.melee}"):
					self.weapon = self.get_weapon_by_name("fist")
					self.current_weapon = self.weapons.index(self.weapon)

			# Switches weapons based on mouse wheel
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 5:
					self.current_weapon -= 1
					if self.current_weapon < 0:
						self.current_weapon = len(self.weapons) - 1
				elif event.button == 4:
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
