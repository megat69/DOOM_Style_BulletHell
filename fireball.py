from sprite_object import SpriteObject
from utils import distance
from settings import SETTINGS

import pygame
from pygame.math import Vector2
from random import uniform, randint
import math


class Fireball(SpriteObject):
	def __init__(
			self,
			game,
			path: str = 'assets/sprites/fireball.png',
			pos: tuple = (10.5, 4.5),
			scale: float = 0.25,
			shift: int = 0.5,
			direction: Vector2 = None,
			noclip: bool = False
	):
		"""
		Creates a fireball.
		:param direction: The direction of the fireball. A 2D vector. Set randomly if None. None by default.
		:param noclip: Whether the fireball clips through walls. False by default.
		"""
		super().__init__(game, path, pos, scale, shift)
		# Lowers the culling distance a ton so the player can still see the fireball even if really close by
		self.culling_distance = 0.1

		# Remembers the direction of the projectile
		self.direction = direction
		if self.direction is None:
			self.direction = Vector2(uniform(-1, 1), uniform(-1, 1)) / randint(200, 400)

		# Remembers whether it clips through walls.
		self.noclip = noclip
		if self.noclip:
			self.image = pygame.image.load('assets/sprites/fireball_blue.png').convert_alpha()


	def check_wall(self, x:int, y:int) -> bool:
		"""
		Checks whether given coordinates are intersecting with a wall within the world map.
		"""
		return (x, y) not in self.game.map.world_map


	def update(self):
		"""
		Called every frame : If the player is colliding with the projectile, we lower their health.
		"""
		super().update()

		# Moves the projectile towards the given direction
		if self.noclip:
			self.x += self.direction.x * self.game.delta_time
			self.y += self.direction.y * self.game.delta_time
		else:
			previous_pos = (self.x, self.y)
			if self.check_wall(int(self.x + self.direction.x * self.SPRITE_SCALE), int(self.y)):
				self.x += self.direction.x * self.game.delta_time
			if self.check_wall(int(self.x), int(self.y + self.direction.y * self.SPRITE_SCALE)):
				self.y += self.direction.y * self.game.delta_time

			# Destroys the projectile if it collided with a wall
			if (self.x, self.y) == previous_pos:
				self.destroy()


		# Finds the distance between the projectile and the player
		if distance(self.game.player.x, self.x, self.game.player.y, self.y) < SETTINGS.player.player_size_scale / 100:
			# Lowers the player health
			self.game.player.health -= 1
			self.game.player.check_health()
			# Removes the projectile from the list of sprites
			self.destroy()

		# If the projectile is out of bounds, destroys it
		if self.x < 0 or self.x > self.game.map.map_size[0] or self.y < 0 or self.y > self.game.map.map_size[1]:
			self.destroy()

		# If the player shot the projectile
		self.check_hit_by_player()


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


	def check_hit_by_player(self):
		"""
		Checks if the entity was hit by the player during a shot.
		"""
		# If the player has shot and the entity can see the player (thus no wall in-between them)
		if self.game.player.shot and self.ray_cast_player_to_entity():
			# If the player shot AT the entity
			if SETTINGS.graphics.resolution[0] // 2 - self.sprite_half_width \
					< self.screen_x < \
					SETTINGS.graphics.resolution[0] // 2 + self.sprite_half_width:
				# We decrease the entity's health by the weapon damage
				for entity in self.game.objects_handler.entities:
					entity_distance = distance(self.x, entity.x, self.y, entity.y)
					# Damages the entity based on the distance
					if entity_distance < 3 and entity.alive:
						entity.health -= 100 / entity_distance
						entity.in_pain = True
				self.destroy()


	def destroy(self):
		"""
		Destroys the projectile.
		"""
		try:
			self.game.objects_handler.sprites_list.remove(self)
		except ValueError: pass
