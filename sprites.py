"""
Contains the created sprites.
"""
# Lib imports
import pygame
import os
import json

# Relative imports
from sprite_object import SpriteObject, AnimatedSprite
from pickups import Pickup, PickupAnimated
from settings import SETTINGS

# Sprite-specific imports
from collections import deque
from weapon import Shotgun


class Candlebra(SpriteObject):
	def __init__(self, game, pos):
		super().__init__(game, path="assets/sprites/candlebra.png", pos=pos)


class GreenFlame(AnimatedSprite):
	def __init__(self, game, pos):
		super().__init__(game, path="assets/animated_sprites/green_flame/0.png", pos=pos)


class ShotgunPickup(Pickup):
	def __init__(self, game, pos):
		super().__init__(
			game, path = 'assets/textures/pickups/shotgun_sprite.png', pos = pos
		)
		# Creates the sound
		self.game.sound.load_sound("shotgun_reload", "assets/sounds/shotgun_reload_long.mp3")


	def pick_up(self):
		"""
		Gives the player the shotgun upon pickup.
		"""
		try:
			# If the shotgun is already in the player's inventory, we refill its ammo'
			shotgun = self.game.get_weapon_by_name("shotgun")
			shotgun.ammo = shotgun.max_ammo
			# TODO : Ammo pick up sound

		# If the shotgun is not in the player's inventory'
		except NameError:
			# Adds the shotgun to the player's inventory
			self.game.weapons.append(
				Shotgun(self.game)
			)

			# Selects the shotgun for the player
			self.game.current_weapon = len(self.game.weapons) - 1
			self.game.weapon = self.game.weapons[self.game.current_weapon]

			# Plays the reload animation once, without a muzzle flash
			def post_rl_func(wpn):
				wpn.images[1] = pygame.image.load(
					"assets/animated_sprites/shotgun/1.png"
				).convert_alpha()
				wpn.images[1] = pygame.transform.smoothscale(
					wpn.images[1],
					(
						wpn.images[1].get_width() * 3,
						wpn.images[1].get_height() * 3
					)
				)
				wpn.animation_time = 70
				wpn.game.player.can_move = True
				wpn.game.sound.load_sound("shotgun_reload", "assets/sounds/shotgun_reload.mp3")
				wpn.game.sound.loaded_sounds["enemy_spawn"].play()

				# Removes the post reload function
				wpn.post_reload_function = lambda x: None
			self.game.weapon.post_reload_function = post_rl_func
			self.game.weapon.images[1] = pygame.image.load(
				"assets/animated_sprites/shotgun_no_muzzle_flash/1.png"
			).convert_alpha()
			self.game.weapon.animation_time = 130
			self.game.player.rel = 0
			self.game.player.can_move = False
			# Also adds enemies to the map
			for i in (1.5, len(self.game.map.map) - 1.5):
				for j in (1.5, len(self.game.map.map[0]) - 1.5):
					self.game.objects_handler.create_enemy(
						pos=(i, j)
					)
			self.game.weapon.reloading = True
			self.game.weapon.animate_shot()


class Portal(PickupAnimated):
	def __init__(self, game, pos, play_sound:bool=True):
		super().__init__(
			game,
			path = "assets/animated_sprites/portal/011.png",
			pos = pos,
			scale = 1.0,
			shift = 0.12
		)
		self.game.sound.load_sound("portal_opening", "assets/sounds/portal_opening.wav")
		if play_sound:
			self.game.sound.loaded_sounds["portal_opening"].play()

	def pick_up(self):
		print("Teleporting to next level")
		self.game.save_data["current_level"] += 1
		with open(os.path.join(SETTINGS.misc.save_location, "save_data.json"), "w") as save_data_file:
			json.dump(self.game.save_data, save_data_file, indent=2)
		self.game.sound.loaded_sounds["portal_opening"].play()
		self.game.await_restart = True


ALL_SPRITES = {
	"candlebra": Candlebra,
	"green_flame": GreenFlame,
	"shotgun_pickup": ShotgunPickup,
	"portal": Portal
}
