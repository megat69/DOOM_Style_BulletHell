import pygame
from pygame.math import Vector2
import math
import os
from collections import deque
import time

from settings import SETTINGS


class SpriteObject:
	def __init__(
		self,
		game,
		path: str = 'assets/sprites/candlebra.png',
		pos: tuple = (10.5, 3.5),
		scale: float = 1.0,
		shift: int = 0.27,
		hidden: bool = False,
		darken: bool = False
	):
		"""
		Creates a new sprite instance.
		:param game: The Game instance.
		:param path: The path to the sprite texture.
		:param pos: The position of the sprite in the level.
		"""
		self.game = game
		self.player = game.player  # Creating a shorthand
		self.x, self.y = pos
		self.image = pygame.image.load(path).convert_alpha()
		self.IMAGE_WIDTH = self.image.get_width()
		self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
		self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
		self.SPRITE_SCALE = scale
		self.SPRITE_HEIGHT_SHIFT = shift
		self.culling_distance = 0.35  # How far away from the camera to cull the sprite
		self.hidden = hidden  # Whether the sprite should be hidden in 2D view
		self.darken = darken  # Whether to darken ythe sprite over distance
		# Initialization of later attributes
		self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 1, 1
		self.sprite_half_width = 0


	def get_sprite(self):
		"""
		Gets the sprite correctly placed in 3D space.
		"""
		# Calculating the angle in which the player will face the sprite (theta angle)
		direction = Vector2(self.x - self.player.x, self.y - self.player.y)
		self.dx, self.dy = direction
		self.theta = math.atan2(direction.y, direction.x)

		# Looks for the delta angle
		delta = self.theta - self.player.angle
		if (direction.x > 0 and self.player.angle > math.pi) or (direction.x < 0 and direction.y < 0):
			delta += math.tau

		# We calculate how many rays are in the delta angle
		delta_rays = delta / SETTINGS.graphics.delta_angle

		# Calculates the Sprite's position based on the last math
		self.screen_x = (SETTINGS.graphics.half_num_rays + delta_rays) * SETTINGS.graphics.scale

		# Calculates the Sprite's size
		self.dist = math.hypot(direction.x, direction.y)
		self.norm_dist = self.dist * math.cos(delta)

		# Only makes further calculations if the sprite is in the visible spectrum
		if -self.IMAGE_HALF_WIDTH < self.screen_x < (SETTINGS.graphics.resolution[0] + self.IMAGE_HALF_WIDTH) and\
				self.norm_dist > self.culling_distance:
			self.get_sprite_projection()


	def get_sprite_projection(self):
		"""
		Gets the projected image of the sprite.
		"""
		proj = SETTINGS.graphics.screen_distance / self.norm_dist * self.SPRITE_SCALE
		# Takes into account different image ratios
		proj_width, proj_height = proj * self.IMAGE_RATIO, proj

		# Scales the sprite to the calculated size
		image = pygame.transform.scale(self.image, (proj_width, proj_height))

		# Finds the sprite's position on the screen
		self.sprite_half_width = proj_width // 2
		height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
		pos = self.screen_x - self.sprite_half_width, SETTINGS.graphics.resolution[1] // 2 - proj_height // 2 + height_shift

		# Adds the sprite to the array of objects to render during raycasting
		self.game.raycasting.objects_to_render.append((
			self.norm_dist,
			image.convert_alpha() if self.darken is False else self.game.raycasting.darken(
				image, self.norm_dist
			),
			pos
		))


	def render_2D_sprite(self):
		"""
		Renders a sprite in 2D mode.
		"""
		if time.time() - self.game.start_time > self.game.map.TITLE_SCREEN_DURATION + self.game.map.TITLE_SCREEN_BLEND_TIME:
			self.game.screen.blit(
				pygame.transform.scale(self.image, (
					SETTINGS.graphics.sprite_size_2D * self.IMAGE_RATIO * self.SPRITE_SCALE,
					SETTINGS.graphics.sprite_size_2D * self.SPRITE_SCALE
				)),
				(
					int(self.x * self.game.map.tile_size) - SETTINGS.graphics.sprite_size_2D * self.SPRITE_SCALE // 2,
					int(self.y * self.game.map.tile_size) - SETTINGS.graphics.sprite_size_2D * self.SPRITE_SCALE // 2
				)
			)

	def update(self):
		"""
		Updates the sprite every frame.
		"""
		if self.game.is_3D:
			self.get_sprite()
		elif self.hidden is False:
			self.render_2D_sprite()


class AnimatedSprite(SpriteObject):
	"""
	A Sprite, but animated.
	"""
	def __init__(
		self,
		game,
		path: str = 'assets/animated_sprites/green_flame/0.png',
		pos: tuple = (11.5, 3.5),
		scale: float = 0.8,
		shift: int = 0.27,
		animation_time: int = 120,
		hidden: bool = False,
		darken: bool = False
	):
		"""
		:param hidden: Whether to show the sprite in 2D.
		:param darken: Whether to use the depth darkening process on this sprite in 3D.
		"""
		# Calls the superclass
		super().__init__(game, path, pos, scale, shift, hidden, darken)
		# Saves the animation time
		self.animation_time = animation_time
		# Saves the path as a list
		self.path = path.rsplit('/', 1)[0]
		# Loads all images in the path
		self.animations = self.get_images(self.path)

		# Remembers the value of the previous animation time and whether to trigger the animation
		self.previous_animation_time = pygame.time.get_ticks()
		self.play_animation = False


	def update(self):
		"""
		Gets called every frame, runs the sprite logic followed by the animation.
		"""
		super().update()
		self.check_animation_time()
		self.animate(self.animations)


	def get_images(self, path:str):
		"""
		Fetches all images in the given folder and returns them.
		"""
		# Initializes a queue
		images = deque()

		# Fetches all images in the given directory
		for filename in os.listdir(path):
			if os.path.isfile(os.path.join(path, filename)):
				# Loads the file into the queue
				images.append(pygame.image.load(os.path.join(path, filename)).convert_alpha())

		# Returns the queue of images
		return images


	def check_animation_time(self):
		"""
		Animates to next frame if the given time has elapsed.
		"""
		self.play_animation = False

		# Gets the current time
		time_now = pygame.time.get_ticks()

		# If it is time to play the next animation frame
		if time_now - self.previous_animation_time > self.animation_time:
			# We play the next frame
			self.previous_animation_time = time_now
			self.play_animation = True


	def animate(self, images):
		"""
		Animates the sprite.
		:param images: The animation frames.
		"""
		if isinstance(images, str):
			images = self.animations[images]

		# If the next frame should be displayed
		if self.play_animation:
			# We rotate the queue and select the next frame as the current frame
			if isinstance(images, deque):
				images.rotate(-1)
				self.image = images[0]


class VFX(SpriteObject):
	def __init__(
		self,
		game,
		path: str = 'assets/animated_sprites/vfx/enemy_spawning/1.png',
		pos: tuple = (11.5, 3.5),
		scale: float = 0.9,
		shift: int = 0.27,
		animation_time: int = 70,
		hidden: bool = True,
		darken: bool = False
	):
		"""
		:param hidden: Whether to show the sprite in 2D.
		:param darken: Whether to use the depth darkening process on this sprite in 3D.
		"""
		# Calls the superclass
		super().__init__(game, path, pos, scale, shift, hidden, darken)
		# Saves the animation time
		self.animation_time = animation_time
		# Saves the path as a list
		self.path = path.rsplit('/', 1)[0]
		# Loads all images in the path
		self.animations = self.get_images(self.path)

		# Remembers the value of the previous animation time and whether to trigger the animation
		self.previous_animation_time = pygame.time.get_ticks()
		self.play_animation = False
		self.current_frame = 0


	def get_images(self, path: str) -> list:
		"""
		Fetches all images in the given folder and returns them.
		"""
		# Initializes a queue
		images = []

		# Fetches all images in the given directory
		for filename in os.listdir(path):
			if os.path.isfile(os.path.join(path, filename)):
				# Loads the file into the queue
				images.append(pygame.image.load(os.path.join(path, filename)).convert_alpha())

		# Returns the queue of images
		return images

	def check_animation_time(self):
		"""
		Animates to next frame if the given time has elapsed.
		"""
		self.play_animation = False

		# Gets the current time
		time_now = pygame.time.get_ticks()

		# If it is time to play the next animation frame
		if time_now - self.previous_animation_time > self.animation_time:
			# We play the next frame
			self.previous_animation_time = time_now
			self.play_animation = True


	def animate(self, images):
		"""
		Animates the sprite.
		:param images: The animation frames.
		"""
		if isinstance(images, str):
			images = self.animations[images]

		# If the next frame should be displayed
		if self.play_animation:
			# We rotate the queue and select the next frame as the current frame
			if isinstance(images, deque):
				images.rotate(-1)
				self.image = images[0]
			elif isinstance(images, list):
				if len(images) > self.current_frame:
					self.image = images[self.current_frame]
					self.current_frame += 1
				else:
					self.game.objects_handler.sprites_list.remove(self)


	def update(self):
		"""
		Gets called every frame, runs the sprite logic followed by the animation.
		"""
		super().update()
		self.check_animation_time()
		self.animate(self.animations)
