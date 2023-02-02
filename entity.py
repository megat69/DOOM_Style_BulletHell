import pygame
import math
from random import randint, choice, uniform
import time
from typing import Tuple, Union

from settings import SETTINGS
from sprite_object import AnimatedSprite
from pickups import Ammo, Health
from utils import distance
from fireball import Fireball


class Entity(AnimatedSprite):
	killed_entities = 0
	def __init__(
			self,
			game,
			path: str = 'assets/entities/soldier/0.png',
			pos: tuple = (11.5, 5.5),
			scale: float = 0.6,
			shift: int = 0.38,
			animation_time: int = 180,
			time_to_fire: Union[Tuple[int, int], int] = (5000, 6000),
			no_ai: bool = False,
			fleer: bool = False
	):
		"""
		:param time_to_fire: The time it takes for the entity to fire an aimed projectile at the player.
		Can be either a tuple of two integers, and an int will be randomly chosen between them, a static integer value.
		:param no_ai: Whether the entity should not possess an AI.
		:param fleer: Whether the entity is a fleer ; if so, will run away from the player instead of coming to them.
		"""
		super().__init__(game, path, pos, scale, shift, animation_time, hidden=True, darken=True)
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
		self.speed = 0.025
		self.size = 10
		self.health = int(100 * (1 + fleer / 4))
		self.alive = True
		self.in_pain = False
		self.can_see_player = False
		self.frame_counter = 0
		self.culling_distance = 0.2
		self.player_far_enough = 0
		self.time_to_fire = randint(
			time_to_fire[0], time_to_fire[1]
		) if isinstance(time_to_fire, tuple) else time_to_fire
		self.inaccuracy = 0.005
		self.shooting_accurate_distance = 3
		self.no_ai = no_ai
		self.fleer = fleer
		self._last_fireball_time = time.time()

		# Loads the pain sound
		self.game.sound.load_sound("pain", self.game.sound.sounds_path + 'npc_pain.wav', "entity")
		self.game.sound.load_sound("death", self.game.sound.sounds_path + 'npc_death.wav', "entity")

	def update(self):
		"""
		Updates the logic of the entity.
		"""
		self.check_animation_time()
		self.run_logic()
		super().update()
		# if distance(self.x, self.player.x, self.y, self.player.y) < self.shooting_accurate_distance \
		# 		and self.game.is_3D is False:
		# 	self.draw_ray_cast(True)
		if self.game.is_3D is False and self.alive:
			pygame.draw.circle(
				self.game.screen,
				(255, 0, 0),
				(
					self.x * self.game.map.tile_size,
					self.y * self.game.map.tile_size
				),
				10
			)

	def check_wall(self, x:int, y:int) -> bool:
		"""
		Checks whether given coordinates are intersecting with a wall within the world map.
		"""
		return (x, y) not in self.game.map.world_map


	def check_wall_collisions(self, direction):
		"""
		Checks if the player is intersecting with a wall.
		"""
		if self.check_wall(int(self.x + direction.x * self.size), int(self.y)):
			self.x += direction.x
		if self.check_wall(int(self.x), int(self.y + direction.y * self.size)):
			self.y += direction.y


	def movement(self, direction: pygame.Vector2 = None):
		"""
		Makes the entity move.
		"""
		# Calculates what the next position is
		if direction is None:
			next_pos = self.game.player.map_pos
			next_x, next_y = next_pos
			angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
			if next_pos in self.game.objects_handler.entity_positions:
				direction = pygame.Vector2(0, 0)
			else:
				direction = pygame.Vector2(math.cos(angle) * self.speed, math.sin(angle) * self.speed)


		# Inverting the direction if the mob is a fleer
		direction *= (-1) ** self.fleer

		# If there is no wall collision and no other entity there already, moves in this direction
		self.check_wall_collisions(direction)


	def run_logic(self):
		"""
		Calculates the logic of the entity.
		"""
		if self.alive:
			# Keeps in mind if the entity can see the player
			self.can_see_player = self.ray_cast_player_to_entity()

			# Checks if the entity was hit
			self.check_hit_by_player()

			# Random chance we spawn a fireball
			if self.player_far_enough <= self.time_to_fire and randint(
					0, len(self.game.objects_handler.entities) * 6) == 0 and (
				time.time() - self._last_fireball_time >= self.game.map.map_data["enemies"]["min_fire_delay"]
			):
				self.game.objects_handler.sprites_list.append(
					Fireball(
						self.game,
						pos=(self.x, self.y),
						direction=pygame.math.Vector2(
							self.player.x - self.x,
							self.player.y - self.y
						).normalize() / 300 + pygame.math.Vector2(
							uniform(-self.inaccuracy, self.inaccuracy),
							uniform(-self.inaccuracy, self.inaccuracy)
						),
						noclip=randint(0, 100) < 5
					)
				)
				self._last_fireball_time = time.time()

			# If the entity was hit by a shot, plays the pain animation
			if self.in_pain:
				self.animate_pain()

			# If it can see the player, plays the walking animation and chases the player
			elif self.can_see_player and not self.no_ai:
				self.animate(self.animations['walk'])
				self.movement()

				# Notices how long the player has been in sight
				if distance(self.x, self.game.player.x, self.y, self.game.player.y) > self.shooting_accurate_distance:
					self.player_far_enough += self.game.delta_time

				# If the player has been close to the entity too long, sending a fireball in his direction
				if self.player_far_enough > self.time_to_fire:
					self.game.objects_handler.sprites_list.append(
						Fireball(
							self.game,
							pos = (self.x, self.y),
							direction = pygame.math.Vector2(
								self.player.x - self.x,
								self.player.y - self.y
							).normalize() / 300 + pygame.math.Vector2(
								uniform(-self.inaccuracy, self.inaccuracy),
								uniform(-self.inaccuracy, self.inaccuracy)
							)
						)
					)
					self.player_far_enough = 0

			# Otherwise, just idles there
			else:
				self.animate(self.animations['idle'])

		else:
			if time.time() - self._death_time > 15:
				self.game.objects_handler.entities.remove(self)
				return None
			self.animate_death()



	def animate_death(self):
		"""
		Animates the entity into a death animation.
		"""
		if not self.alive:
			if self.play_animation and self.frame_counter < len(self.animations["death"]) - 1:
				self.animations["death"].rotate(-1)
				self.image = self.animations["death"][0]
				self.frame_counter += 1


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
		# If the player has shot and the entity can see the player (thus no wall in-between them)
		if self.game.player.shot and self.can_see_player:
			# If the player shot AT the entity
			if SETTINGS.graphics.resolution[0] // 2 - self.sprite_half_width \
					< self.screen_x < \
					SETTINGS.graphics.resolution[0] // 2 + self.sprite_half_width:

				# We play the pain sound
				self.game.sound.loaded_sounds["pain"].play()
				self.in_pain = True

				# We decrease the entity's health by the weapon damage
				self.health -= self.game.weapon.get_damage(
					# We calculate the distance between the entity and the player
					distance(self.x, self.game.player.x, self.y, self.game.player.y)
				)
				self.check_health()


	def check_health(self):
		"""
		Checks if the entity is still alive.
		"""
		# Kills the entity if the health drops below zero
		if self.health < 1:
			self.alive = False
			self.game.sound.loaded_sounds["death"].play()
			# Counts the dead
			Entity.killed_entities += 1
			# Creates the death time
			self._death_time = time.time()
			# Gives the player ammo
			if self.game.weapon.name != "fist":
				self.game.objects_handler.add_sprite(
					Ammo(
						self.game, f'assets/textures/pickups/{self.game.weapon.name}.png',
						(self.x, self.y), self.game.weapon.name, randint(
							Ammo.BASE_GAIN[self.game.weapon.name][0],
							Ammo.BASE_GAIN[self.game.weapon.name][1]
						)
					)
				)
			else:
				if randint(0, 1) == 0:
					self.game.objects_handler.add_sprite(
						Health(
							self.game,
							pos=(self.x, self.y)
						)
					)
				if randint(0, 2) != 2:
					if not all(weapon.name == "fist" for weapon in self.game.weapons):
						chosen_weapon = choice(self.game.weapons)
						while chosen_weapon is self.game.get_weapon_by_name("fist"):
							chosen_weapon = choice(self.game.weapons)
						self.game.objects_handler.add_sprite(
							Ammo(
								self.game, f'assets/textures/pickups/{chosen_weapon.name}.png',
								(self.x, self.y), chosen_weapon.name, randint(
									Ammo.BASE_GAIN[chosen_weapon.name][0],
									Ammo.BASE_GAIN[chosen_weapon.name][1]
								)
							)
						)

	@property
	def map_pos(self):
		return int(self.x), int(self.y)


	def ray_cast_player_to_entity(self) -> bool:
		"""
		Casts a ray in every direction from the player's FOV to render the map.
		"""
		# If the player is in the same tile as the entity
		if self.game.player.map_pos == self.map_pos:
			return True

		# Keeps in mind the distances to the walls (for the player and the npc)
		wall_distance_vertical, wall_distance_horizontal = 0, 0
		player_distance_vertical, player_distance_horizontal = 0, 0

		# Original position of the player on the map at the start of the frame
		original_position_x, original_position_y = self.game.player.pos
		# Coordinates of the tile the player is on
		map_position_x, map_position_y = self.game.player.map_pos

		# Calculates the angle of the raycast, based on the player's rotation angle, half FOV, and a small value to
		# avoid divisions by zero
		ray_angle = self.theta

		# Precalculates the sine and cosine of the ray's angle
		sin_a, cos_a = math.sin(ray_angle), math.cos(ray_angle)
		if sin_a == 0:
			sin_a = 1e-6
		if cos_a == 0:
			cos_a = 1e-6

		# Determines the intersections of horizontal tiles
		horizontal_y, direction_y = (map_position_y + 1, 1) if sin_a > 0 else (map_position_y - 1e-6, -1)

		# Calculates the depth of the horizontal
		depth_horizontal = (horizontal_y - original_position_y) / sin_a
		horizontal_x = original_position_x + depth_horizontal * cos_a

		# Calculates the depth
		delta_depth = direction_y / sin_a
		direction_x = delta_depth * cos_a

		# Looping for each vertical up to the maximum depth
		for i in range(SETTINGS.graphics.max_depth):
			tile_hor = int(horizontal_x), int(horizontal_y)
			# If we found the player position
			if tile_hor == self.map_pos:
				player_distance_horizontal = depth_horizontal
				break
			# If we found a wall, we stop the cycle
			if tile_hor in self.game.map.world_map:
				wall_distance_horizontal = depth_horizontal
				break

			# Otherwise, we keep going
			horizontal_x += direction_x
			horizontal_y += direction_y
			depth_horizontal += delta_depth

		# Determines the intersections with the vertical tiles
		vertical_x, direction_x = (map_position_x + 1, 1) if cos_a > 0 else (map_position_x - 1e-6, -1)

		# Calculates the depth of the vertical
		depth_vertical = (vertical_x - original_position_x) / cos_a
		vertical_y = original_position_y + depth_vertical * sin_a

		# Calculates the depth
		delta_depth = direction_x / cos_a
		direction_y = delta_depth * sin_a

		# Looping for each vertical up to the maximum depth
		for i in range(SETTINGS.graphics.max_depth):
			tile_vert = int(vertical_x), int(vertical_y)
			# If we found the player position
			if tile_vert == self.map_pos:
				player_distance_vertical = depth_vertical
				break
			# If we found a wall, we stop the cycle
			if tile_vert in self.game.map.world_map:
				wall_distance_vertical = depth_vertical
				break

			# Otherwise, we keep going
			vertical_x += direction_x
			vertical_y += direction_y
			depth_vertical += delta_depth

		# Gets the max values between the distance to the player and the distance to the wall
		player_distance = max(player_distance_vertical, player_distance_horizontal)
		wall_distance = max(wall_distance_vertical, wall_distance_horizontal)

		# Returns whether there is a direct line of sight between the NPC and the player
		if 0 < player_distance < wall_distance or not wall_distance:
			return True
		else:
			return False

	def draw_ray_cast(self, normalized_ray_only: bool = False):
		if not normalized_ray_only:
			pygame.draw.circle(
				self.game.screen, 'red', (
					self.game.map.tile_size * self.x,
					self.game.map.tile_size * self.y
				), 15
			)

		if self.ray_cast_player_to_entity():
			pygame.draw.line(
				self.game.screen, 'red', (
					self.game.map.tile_size * self.player.x,
					self.game.map.tile_size * self.player.y
				), (
					self.game.map.tile_size * self.x,
					self.game.map.tile_size * self.y
				), 2
			)
