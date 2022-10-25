import pygame
import os

from settings import SETTINGS


class Sound:
	"""
	Handles all audio in the game.
	"""
	def __init__(self, game):
		self.game = game
		# Initializes the sound mixer
		pygame.mixer.init()  # TODO : Audio output device
		# Remembers the path to the sound ressources and the loaded sounds
		self.sounds_path = 'assets/sounds/'
		self.loaded_sounds = {}


	def load_sound(self, name:str, path:str, category:str="sfx"):
		"""
		Loads a sound with the correct volume, name, and path.
		:param name: The name of the sound in the loaded_sounds dict.
		:param path: The path to the sound file.
		:param category: The category of the sound. Can be 'sfx', 'weapon', 'entity'. Default is 'sfx'.
		"""
		# Checks if the sound is in the existing categories
		if category not in ('sfx', 'weapon', 'entity'):
			raise ValueError(f"Category {category} does not exist.")

		# Loads the sound
		self.loaded_sounds[name] = pygame.mixer.Sound(path)

		# Sets the correct volume to it
		self.loaded_sounds[name].set_volume(SETTINGS.sound.master * getattr(SETTINGS.sound, category))