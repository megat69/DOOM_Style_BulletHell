import pygame
import math

from settings import SETTINGS


class RayCasting:
	"""
	Main engine of the game for the raycasts. Generates the pseudo3D and the 2D
	"""
	def __init__(self, game):
		"""
		:param game: The instance of the Game.
		"""
		self.game = game


	def ray_cast(self):
		"""
		Casts a ray in every direction from the player's FOV to render the map.
		"""
		# Original position of the player on the map at the start of the frame
		original_position_x, original_position_y = self.game.player.pos
		# Coordinates of the tile the player is on
		map_position_x, map_position_y = self.game.player.map_pos

		# Calculates the angle of the raycast, based on the player's rotation angle, half FOV, and a small value to
		# avoid divisions by zero
		ray_angle = self.game.player.angle - SETTINGS.graphics.fov / 2 + 0.0001

		# Raycasts n times where n is the amount of rays we want to cast
		for ray in range(SETTINGS.graphics.num_rays):
			# Precalculates the sine and cosine of the ray's angle
			sin_a, cos_a = math.sin(ray_angle), math.cos(ray_angle)

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

				# If we found a wall, we stop the cycle
				if tile_hor in self.game.map.world_map:
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

				# If we found a wall, we stop the cycle
				if tile_vert in self.game.map.world_map:
					break

				# Otherwise, we keep going
				vertical_x += direction_x
				vertical_y += direction_y
				depth_vertical += delta_depth

			# We keep as final depth the smallest depth between the vertical and horizontal lines
			depth = min(depth_vertical, depth_horizontal)

			# Draws the raycast for debug purposes
			pygame.draw.line(
				self.game.screen,
				'yellow',
				(100 * original_position_x, 100 * original_position_y),
				(100 * original_position_x + 100 * depth * cos_a, 100 * original_position_y + 100 * depth * sin_a),
				2
			)

			# Calculates the angle of the ray
			ray_angle += SETTINGS.graphics.delta_angle


	def update(self):
		"""
		Gets called every frame, runs the engine logic.
		"""
		self.ray_cast()
