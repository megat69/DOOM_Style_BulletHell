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
			scale: float = 0.4,
			animation_time: int = 80
	):
		super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
		# Loads the images
		self.images = deque(
			[
				pygame.transform.smoothscale(
					img,
					(
						self.image.get_width() * scale,
						self.image.get_height() * scale
					)
				) for img in self.images
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
		# We keep in mind the weapon's damage
		self.damage = 50
		# Loads the shotgun sound
		self.game.sound.load_sound("shotgun", os.path.join(self.game.sound.sounds_path, "shotgun.wav"), "weapon")


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