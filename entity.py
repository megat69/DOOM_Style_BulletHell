import pygame

from settings import SETTINGS
from sprite_object import AnimatedSprite


class Entity(AnimatedSprite):
	def __init__(
			self,
			game,
			path: str = 'assets/entities/soldier/0.png',
			pos: tuple = (11.5, 5.5),
			scale: float = 0.6,
			shift: int = 0.38,
			animation_time: int = 180
	):
		super().__init__(game, path, pos, scale, shift, animation_time)
		# Loads all images for each state
		self.animations = {
			'attack': self.get_images(self.path + '/attack'),
			'death': self.get_images(self.path + '/death'),
			'idle': self.get_images(self.path + '/idle'),
			'pain': self.get_images(self.path + '/pain'),
			'walk': self.get_images(self.path + '/walk'),
		}

		# Entity parameters
		self.attack_distance = 20
		self.speed = 0.035
		self.size = 10
		self.health = 100
		self.alive = True
		self.in_pain = False
		self.raycast_hit = False

		# Loads the pain sound
		self.game.sound.load_sound("pain", self.game.sound.sounds_path + 'npc_pain.wav', "entity")

	def update(self):
		"""
		Updates the logic of the entity.
		"""
		self.check_animation_time()
		self.run_logic()
		super().update()


	def run_logic(self):
		"""
		Calculates the logic of the entity.
		"""
		if self.alive:
			# Checks if the entity was hit
			self.check_hit_by_player()
			if self.in_pain:
				self.animate_pain()
			else:
				self.animate(self.animations['idle'])


	def animate_pain(self):
		"""
		Animates the entity into pain.
		"""
		self.animate(self.animations['pain'])
		if self.play_animation:
			self.in_pain = False


	def check_hit_by_player(self):
		"""
		Checks if the entity was hit by the player during a shot.
		"""
		if self.game.player.shot:
			if SETTINGS.graphics.resolution[0] // 2 - self.sprite_half_width \
					< self.screen_x < \
					SETTINGS.graphics.resolution[0] // 2 + self.sprite_half_width:
				self.game.sound.loaded_sounds["pain"].play()
				self.in_pain = True


	@property
	def map_pos(self):
		return int(self.x), int(self.y)
