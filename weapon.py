import os
import pygame
from collections import deque

from settings import SETTINGS
from sprite_object import AnimatedSprite


class Weapon(AnimatedSprite):
	"""
	The Shotgun to kill your opponents.
	"""
	def __init__(
			self,
			game,
			path: str = 'assets/animated_sprites/shotgun/0.png',
			scale: float = 3,
			animation_time: int = 80,
			name: str = "shotgun",
			starting_ammo: int = 18,
			max_ammo: int = 18,
			speed_multiplier: float = 0.75
	):
		super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
		# Loads the images
		self.images = deque(
			[
				pygame.transform.smoothscale(
					img,
					(
						img.get_width() * scale,
						img.get_height() * scale
					)
				) for img in self.animations
			]
		)
		# Gets the position to center the weapon on the screen
		self.weapon_pos = (
			SETTINGS.graphics.resolution[0] // 2 - self.images[0].get_width() // 2,
			SETTINGS.graphics.resolution[1] - self.images[0].get_height()
		)
		# Remembers whether we are reloading
		self.reloading = False
		# Remembers the amount of animation frames we have and which we are on
		self.num_frames = len(self.images)
		self.frame_counter = 0
		# Loads the shotgun sound
		self.game.sound.load_sound(name, os.path.join(self.game.sound.sounds_path, f"{name}.wav"), "weapon")
		self.sound = self.game.sound.loaded_sounds[name]
		# Keeps the ammo count
		self._ammo = starting_ammo
		self.max_ammo = max_ammo
		# Keeps the name of the weapon
		self.name = name
		# Keeps the speed multiplier
		self.speed_multiplier = speed_multiplier


	def get_damage(self, distance: float) -> float:
		"""
		Returns the weapon's damage over range.
		"""
		return max(23, 50 / distance)


	def animate_shot(self):
		"""
		Animates the weapon after the player has shot.
		"""
		# If we are reloading
		if self.reloading:
			# We set the player's shot value to False
			self.game.player.shot = False

			# If the animation is playing, we perform the animation
			if self.play_animation:
				self.images.rotate(-1)
				self.image = self.images[0]
				self.weapon_pos = (
					SETTINGS.graphics.resolution[0] // 2 - self.images[0].get_width() // 2,
					SETTINGS.graphics.resolution[1] - self.images[0].get_height()
				)
				self.frame_counter += 1

				# If the animation is over, we reset its properties
				if self.frame_counter == self.num_frames:
					self.reloading = False
					self.frame_counter = 0


	def draw(self):
		"""
		Draws the weapon if in 3D.
		"""
		self.game.screen.blit(self.images[0], self.weapon_pos)


	def update(self):
		"""
		Updates the animation properties.
		"""
		self.check_animation_time()
		self.animate_shot()

	@property
	def ammo(self):
		return self._ammo

	@ammo.setter
	def ammo(self, value: int):
		self._ammo = value


class Shotgun(Weapon):
	"""
	The shotgun.
	"""
	def __init__(self, game):
		super().__init__(
			game, 'assets/animated_sprites/shotgun/0.png', 4, 70,
			"shotgun",
			starting_ammo=18,
			max_ammo=18,
			speed_multiplier=0.95
		)

	def get_damage(self, distance: float) -> float:
		return max(23, 70 / distance)


class Pistol(Weapon):
	"""
	A pistol.
	"""
	def __init__(self, game):
		super().__init__(
			game, 'assets/animated_sprites/pistol/0.png', 3, 40,
			name="pistol",
			starting_ammo=24,
			max_ammo=24,
			speed_multiplier=1.02
		)

	def get_damage(self, distance: float) -> float:
		"""
		The damage of the pistol.
		"""
		return 33 - distance


class Fist(Weapon):
	def __init__(self, game):
		super().__init__(
			game, 'assets/animated_sprites/fists/0.png', 3, 30,
			name="fist",
			starting_ammo=1,
			max_ammo=1,
			speed_multiplier=1.1
		)

	def get_damage(self, distance: float) -> float:
		return 100 if distance < 0.75 else 0

	def animate_shot(self):
		"""
		Animates the weapon after the player has tried to hit the enemy.
		"""
		# If we are reloading
		if self.reloading:
			# We set the player's shot value to False
			self.game.player.shot = False

			# If the animation is playing, we perform the animation
			if self.play_animation:
				self.images.rotate(-1)
				self.image = self.images[0]
				self.weapon_pos = (
					SETTINGS.graphics.resolution[0] // 2 - self.images[0].get_width() // 2,
					SETTINGS.graphics.resolution[1] - self.images[0].get_height()
				)
				self.frame_counter += 1

				# If the animation is over, we reset its properties
				if self.frame_counter == self.num_frames:
					self.ammo += 1
					self.reloading = False
					self.frame_counter = 0
					# Sets the weapon back to the current weapon
					self.game.weapon = self.game.weapons[self.game.current_weapon]