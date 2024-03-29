import pygame
from pygame.math import Vector2
import math

from settings import SETTINGS


class Player:
	"""
	The Player of the game.
	"""
	def __init__(self, game):
		"""
		Controls the player.
		:param game: An instance of the Game.
		"""
		self.game = game

		# Keeping in mind the player coords
		self.x, self.y = self.game.map.map_data["player_start_pos"]
		self.angle = SETTINGS.player.angle

		# Keeping in mind if the player is moving
		self.is_moving = False
		self.can_move = True  # Whether the player is allowed to move

		# Keeps track of the player's health by setting it to the base health (setting)
		self.health = SETTINGS.player.base_health

		# Keeping in mind whether the player has shot
		self.shot = False


	def movement_3D(self):
		"""
		Makes the player move
		"""
		if self.health < 1 or not self.can_move: return
		# Determines the vector the player should follow to move forward
		sin_a = math.sin(self.angle)
		cos_a = math.cos(self.angle)

		# The player's direction vector
		direction = Vector2(0)

		# Calculating the player's speed based on its default speed and the delta time
		speed = SETTINGS.player.speed * self.game.weapon.speed_multiplier * self.game.delta_time

		# Precalculating the values of sine and cosine of the speed and angle
		speed_sin = speed * sin_a
		speed_cos = speed * cos_a

		# Gets the keys currently pressed
		keys = pygame.key.get_pressed()
		if keys[getattr(pygame, f"K_{SETTINGS.controls.forward}")]:
			direction.x += speed_cos
			direction.y += speed_sin
		if keys[getattr(pygame, f"K_{SETTINGS.controls.backward}")]:
			direction.x -= speed_cos
			direction.y -= speed_sin
		if keys[getattr(pygame, f"K_{SETTINGS.controls.left}")]:
			direction.x += speed_sin
			direction.y -= speed_cos
		if keys[getattr(pygame, f"K_{SETTINGS.controls.right}")]:
			direction.x -= speed_sin
			direction.y += speed_cos

		# Keeps in mind whether the player is moving
		self.is_moving = direction != Vector2(0)

		# Uses the calculated information to make the player move
		self.check_wall_collisions(direction)

		# Makes the player rotate
		self._rotate_player_from_keys(keys)

	def movement_2D(self):
		if self.health < 1 or not self.can_move: return
		# The player's direction vector
		direction = Vector2(0)

		# Gets the keys currently pressed
		keys = pygame.key.get_pressed()
		if keys[getattr(pygame, f"K_{SETTINGS.controls.forward}")]:
			direction.y -= 1
		if keys[getattr(pygame, f"K_{SETTINGS.controls.backward}")]:
			direction.y += 1
		if keys[getattr(pygame, f"K_{SETTINGS.controls.left}")]:
			direction.x -= 1
		if keys[getattr(pygame, f"K_{SETTINGS.controls.right}")]:
			direction.x += 1

		# Calculating the player's speed based on its default speed and the delta time
		speed = SETTINGS.player.speed * self.game.delta_time

		# Multiplies the direction by the delta time
		direction *= speed

		# Remembers if the player is moving
		self.is_moving = direction != Vector2(0)

		# Uses the calculated information to make the player move
		self.check_wall_collisions(direction)

		# Head rotation
		self._rotate_player_from_keys(keys)


	def _rotate_player_from_keys(self, keys):
		if keys[pygame.K_LEFT]:
			self.angle -= SETTINGS.player.rotation_speed * self.game.delta_time
		if keys[pygame.K_RIGHT]:
			self.angle += SETTINGS.player.rotation_speed * self.game.delta_time
		self.angle %= math.tau


	def check_wall(self, x:int, y:int) -> bool:
		"""
		Checks whether given coordinates are intersecting with a wall within the world map.
		"""
		return (x, y) not in self.game.map.world_map


	def check_wall_collisions(self, direction:Vector2):
		"""
		Checks if the player is intersecting with a wall.
		"""
		scale = SETTINGS.player.player_size_scale / self.game.delta_time
		if self.check_wall(int(self.x + direction.x * scale), int(self.y)):
			self.x += direction.x
		if self.check_wall(int(self.x), int(self.y + direction.y * scale)):
			self.y += direction.y


	def draw(self):
		"""
		Draws the player on the map.
		"""
		if self.game.is_3D is False:
			pygame.draw.line(
				self.game.screen,
				'yellow',
				(self.x * self.game.map.tile_size, self.y * self.game.map.tile_size),
				(
					self.x * self.game.map.tile_size + 50 * math.cos(self.angle),
					self.y * self.game.map.tile_size + 50 * math.sin(self.angle)
				),
				2
			)
			pygame.draw.circle(
				self.game.screen,
				'green',
				(self.x * self.game.map.tile_size, self.y * self.game.map.tile_size),
				15
			)


	def mouse_control(self):
		"""
		Controls the player using the mouse in 3D.
		"""
		mx, my = pygame.mouse.get_pos()
		if mx < SETTINGS.controls.mouse_border_left or mx > SETTINGS.controls.mouse_border_right:
			pygame.mouse.set_pos([SETTINGS.graphics.half_width, SETTINGS.graphics.half_height])
		self.rel = pygame.mouse.get_rel()[0]
		self.rel = max(-SETTINGS.controls.mouse_max_rel, min(SETTINGS.controls.mouse_max_rel, self.rel))
		self.rel *= 1 + 4 * (not self.game.is_3D)
		self.angle += self.rel * SETTINGS.controls.sensitivity * self.game.delta_time


	def single_fire_event(self, event):
		"""
		Fires if the player presses the left mouse button or the fire key, and can shoot.
		"""
		if ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or
				(event.type == pygame.KEYDOWN and event.key == getattr(pygame, f"K_{SETTINGS.controls.fire}"))) \
				and (self.shot or self.game.weapon.reloading) is False and self.game.weapon.ammo > 0:
			self.shot = True
			self.game.weapon.reloading = True
			# Plays the firing sound
			self.game.weapon.sound.play()
			# Removes ammo from the gun
			self.game.weapon.ammo -= 1


	def check_health(self):
		"""
		Checks the player health.
		"""
		if self.health < 1:
			self.game.UI.create_UI_element(
				"dead", "DEAD", "Impact", 128, lambda x, y: None,
				(SETTINGS.graphics.resolution[0] // 2, SETTINGS.graphics.resolution[1] // 2 - 50),
				(255, 255, 255), True
			)


	def update(self):
		"""
		Runs every frame to determine the player's logic.
		"""
		# Makes the player move correctly
		if self.game.is_3D:
			self.movement_3D()
		else:
			self.movement_2D()

		if self.can_move:
			self.mouse_control()


	@property
	def pos(self):
		""" Returns the player's position """
		return self.x, self.y

	@property
	def map_pos(self):
		""" Returns the position of the tile the player is currently standing on """
		return int(self.x), int(self.y)
