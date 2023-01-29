import pygame
import math

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
		self.can_see_player = False
		self.frame_counter = 0

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
		# self.draw_ray_cast()


	def run_logic(self):
		"""
		Calculates the logic of the entity.
		"""
		if self.alive:
			# Keeps in mind if the entity can see the player
			self.can_see_player = self.ray_cast_player_to_entity()

			# Checks if the entity was hit
			self.check_hit_by_player()
			if self.in_pain:
				self.animate_pain()
			else:
				self.animate(self.animations['idle'])

		else:
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
				self.health -= self.game.weapon.damage
				self.check_health()


	def check_health(self):
		"""
		Checks if the entity is still alive.
		"""
		if self.health < 1:
			self.alive = False
			self.game.sound.loaded_sounds["death"].play()

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

	def draw_ray_cast(self):
		pygame.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
		if self.ray_cast_player_to_entity():
			pygame.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y), (100 * self.x, 100 * self.y), 2)