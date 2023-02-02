import time

from settings import SETTINGS
from sprite_object import SpriteObject, AnimatedSprite


class Pickup(SpriteObject):
	def __init__(
			self,
			game,
			path: str = 'assets/textures/pickups/pistol.png',
			pos: tuple = (10.5, 4.5),
			scale: float = 0.1,
			shift: int = 5,
			pickup_distance: float = .25
	):
		super().__init__(game, path, pos, scale, shift)
		self.picked_up = False
		self.pickup_distance = pickup_distance
		self._creation_time = time.time()

	def update(self):
		"""
		Calls the sprite update method along with the pickup behaviour.
		"""
		super().update()
		if (round(self.player.x, 1) - self.pickup_distance < self.x < round(self.player.x, 1) + self.pickup_distance) and \
				(round(self.player.y, 1) - self.pickup_distance < self.y < round(self.player.y, 1) + self.pickup_distance):
			if self.picked_up is False:
				self.pick_up()
				self.game.objects_handler.sprites_list.remove(self)


	def pick_up(self):
		"""
		Picks up the pickup item.
		"""
		pass


class PickupAnimated(AnimatedSprite):
	def __init__(
			self,
			game,
			path: str = 'assets/textures/pickups/pistol.png',
			pos: tuple = (10.5, 4.5),
			scale: float = 0.1,
			shift: int = 5,
			pickup_distance: float = .25,
			animation_time: int = 120
	):
		super().__init__(game, path, pos, scale, shift, animation_time)
		self.picked_up = False
		self.pickup_distance = pickup_distance
		self._creation_time = time.time()


	def update(self):
		super().update()
		if (round(self.player.x, 1) - self.pickup_distance < self.x < round(self.player.x, 1) + self.pickup_distance) and \
				(round(self.player.y, 1) - self.pickup_distance < self.y < round(self.player.y, 1) + self.pickup_distance):
			if self.picked_up is False:
				self.pick_up()
				try:
					self.game.objects_handler.sprites_list.remove(self)
				except ValueError: pass

	def pick_up(self):
		pass

class Ammo(Pickup):
	BASE_GAIN = {
		"pistol": (2, 5),
		"shotgun": (1, 2),
		"fist": (0, 0)
	}
	def __init__(
			self,
			game,
			path: str = 'assets/textures/pickups/pistol.png',
			pos: tuple = (10.5, 4.5),
			ammo_type: str = "pistol",
			ammo_gain: int = 4,
			time_to_disappear: int = 30
	):
		super().__init__(game, path, pos, 0.1, 5)
		self.ammo_type = ammo_type
		self.ammo_gain = ammo_gain
		self.time_to_disappear = time_to_disappear  # If set to None, will not disappear
		self._creation_time = time.time()


	def update(self):
		"""
		Updates the game.
		"""
		if self.game.is_3D:
			self.get_sprite()
		elif self.hidden is False:
			self.render_2D_sprite()

		# Destroys the entity
		if self.time_to_disappear is not None and \
				time.time() - self._creation_time > self.time_to_disappear:
			self.game.objects_handler.sprites_list.remove(self)
			return None

		# Picks up ammo
		if (round(self.player.x, 1) - self.pickup_distance < self.x < round(self.player.x, 1) + self.pickup_distance) and \
				(round(self.player.y, 1) - self.pickup_distance < self.y < round(self.player.y, 1) + self.pickup_distance):
			# Gets the currently used weapon
			ammo_weapon = self.game.get_weapon_by_name(self.ammo_type)
			# If the ammo capacity for this gun is not full, we pickup the ammo
			if self.picked_up is False and ammo_weapon.ammo < ammo_weapon.max_ammo:
				self.pick_up()
				self.game.objects_handler.sprites_list.remove(self)


	def pick_up(self):
		"""
		Picks up the ammo.
		"""
		# Finds the correct gun on which to add the ammo
		weapon = self.game.get_weapon_by_name(self.ammo_type)
		weapon.ammo += self.ammo_gain
		weapon.ammo = min(weapon.ammo, weapon.max_ammo)


class Health(Pickup):
	def __init__(
			self,
			game,
			path: str = 'assets/textures/pickups/health_pack.png',
			pos: tuple = (10.5, 4.5),
			health_gain: int = 1,
			time_to_disappear: int = 30
	):
		super().__init__(game, path, pos, 0.1, 5)
		self.health_gain = health_gain
		self.time_to_disappear = time_to_disappear  # If set to None, will not disappear
		self._creation_time = time.time()

	def update(self):
		"""
		Updates the game.
		"""
		if self.game.is_3D:
			self.get_sprite()
		elif self.hidden is False:
			self.render_2D_sprite()

		# Destroys the entity
		if self.time_to_disappear is not None and \
				time.time() - self._creation_time > self.time_to_disappear:
			self.game.objects_handler.sprites_list.remove(self)
			return None

		# Picks up the health
		if (round(self.player.x, 1) - self.pickup_distance < self.x < round(self.player.x, 1) + self.pickup_distance) and \
				(round(self.player.y, 1) - self.pickup_distance < self.y < round(self.player.y, 1) + self.pickup_distance):
			# If the ammo capacity for this gun is not full, we pickup the ammo
			if self.picked_up is False and self.game.player.health < SETTINGS.player.base_health:
				self.pick_up()
				self.game.objects_handler.sprites_list.remove(self)


	def pick_up(self):
		"""
		Picks up the ammo.
		"""
		# Gives the player health
		self.game.player.health += self.health_gain
		self.game.player.health = min(self.game.player.health, SETTINGS.player.base_health)
