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

		# The results of raycasting
		self.ray_casting_result = []

		# The objects to render
		self.objects_to_render = []

		# A pointer towards the wall textures
		self.wall_textures = self.game.object_renderer.wall_textures

		self._masking_surface = self.game.screen.copy()


	def get_objects_to_render(self):
		"""
		Gets all objects to render.
		"""
		self.objects_to_render.clear()

		# Fetches all raycast results
		for ray, values in enumerate(self.ray_casting_result):
			# Unpacks the result
			depth, projection_height, texture, offset = values

			# Gets the correct subportion of the wall to render
			if projection_height < SETTINGS.graphics.resolution[1]:  # Normal execution if we're not too close to the wall
				wall_column = self.wall_textures[texture].subsurface(
					offset * (SETTINGS.graphics.texture_size - SETTINGS.graphics.scale),
					0,
					SETTINGS.graphics.scale,
					SETTINGS.graphics.texture_size
				)

				# Calculates the correct column of the wall to render at the right size
				wall_column = pygame.transform.scale(wall_column, (SETTINGS.graphics.scale, projection_height))
				wall_pos = (ray * SETTINGS.graphics.scale, SETTINGS.graphics.half_height - projection_height // 2)

			else:  # If the size of the wall exceeds the window's height
				texture_height = SETTINGS.graphics.texture_size * SETTINGS.graphics.resolution[1] / projection_height
				wall_column = self.wall_textures[texture].subsurface(
					offset * (SETTINGS.graphics.texture_size - SETTINGS.graphics.scale),
					SETTINGS.graphics.half_texture_size - texture_height // 2,
					SETTINGS.graphics.scale,
					texture_height
				)

				# Calculates the correct column of the wall to render at the right size
				wall_column = pygame.transform.scale(wall_column, (SETTINGS.graphics.scale, SETTINGS.graphics.resolution[1]))
				wall_pos = (ray * SETTINGS.graphics.scale, 0)

			# Darkens the wall column based on its distance with the camera
			wall_column = self.darken(wall_column, depth)

			# Adds the object to the list of objects to render
			self.objects_to_render.append((depth, wall_column, wall_pos))


	def darken(self, surf: pygame.Surface, depth: float, multiplier: float = 2) -> pygame.Surface:
		"""
		Returns a darkened version of the given surface based on the depth.
		:param surf: The surface to darken.
		:param depth: The depth at which the surface will be placed in 3D space.
		:param multiplier: The darkening multiplier, default is 2.
		:return: The darkened surface.
		"""
		# Uses a darkening method, heavy on the CPU
		if SETTINGS.graphics.advanced_depth_darkening:
			# Creates a surface with a special tag with the size of the given surface
			darkener = pygame.Surface(surf.get_size(), flags=pygame.SRCALPHA)

			# Remembers how much this is to darken
			darkening_depth = depth * multiplier  # Adjust based on liking, found 2 to be subtle but effective

			# Darkens the darkening surface
			darkener.fill((darkening_depth, darkening_depth, darkening_depth, 0))

			# Blits the darkener on top of the base surface, essentially making it darker
			surf.blit(darkener, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

		# Returns the surface
		return surf


	def ray_cast(self):
		"""
		Casts a ray in every direction from the player's FOV to render the map.
		"""
		# Clears the last raycasting result
		self.ray_casting_result.clear()

		# Original position of the player on the map at the start of the frame
		original_position_x, original_position_y = self.game.player.pos
		# Coordinates of the tile the player is on
		map_position_x, map_position_y = self.game.player.map_pos

		# Texture coordinates
		texture_vertical, texture_horizontal = 1, 1

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
					texture_horizontal = self.game.map.world_map[tile_hor]
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
					texture_vertical = self.game.map.world_map[tile_vert]
					break

				# Otherwise, we keep going
				vertical_x += direction_x
				vertical_y += direction_y
				depth_vertical += delta_depth

			# We keep as final depth the smallest depth between the vertical and horizontal lines, as well as
			# the texture coordinates
			if depth_vertical < depth_horizontal:
				depth, texture = depth_vertical, texture_vertical
				vertical_y %= 1
				offset = vertical_y if cos_a > 0 else (1 - vertical_y)
			else:
				depth, texture = depth_horizontal, texture_horizontal
				horizontal_x %= 1
				offset = (1 - horizontal_x) if sin_a > 0 else horizontal_x

			# Removing fishbowl effect
			depth *= math.cos(self.game.player.angle - ray_angle)

			# Projection mapping
			projection_height = SETTINGS.graphics.screen_distance / (depth + 0.0001)  # Tiny margin not to divide by zero

			# Walls drawing
			if self.game.is_3D:
				self.ray_casting_result.append(
					(depth, projection_height, texture, offset)
				)

			# Draws the raycast for debug purposes
			# if self.game.is_3D is False:
			# 	pygame.draw.line(
			# 		self._masking_surface,
			# 		'white',
			# 		(
			# 			SETTINGS.graphics.tile_size * original_position_x,
			# 			SETTINGS.graphics.tile_size * original_position_y
			# 		),
			# 		(
			# 			SETTINGS.graphics.tile_size * original_position_x + SETTINGS.graphics.tile_size * depth * cos_a,
			# 			SETTINGS.graphics.tile_size * original_position_y + SETTINGS.graphics.tile_size * depth * sin_a
			# 		),
			# 		2
			# 	)

			# Calculates the angle of the ray
			ray_angle += SETTINGS.graphics.delta_angle


	def update(self):
		"""
		Gets called every frame, runs the engine logic.
		"""
		self.ray_cast()
		self.get_objects_to_render()
