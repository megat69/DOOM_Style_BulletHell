from sprite_object import SpriteObject, AnimatedSprite, Fireball


class ObjectHandler:
	"""
	Handles all objects in the game.
	"""
	def __init__(self, game):
		self.game = game
		self.sprites_list = []
		self.static_sprites_path = 'assets/sprites/'
		self.animated_sprites_path = "assets/animated_sprites/"

		# Sprite creation
		self.add_sprite(SpriteObject(game))
		self.add_sprite(AnimatedSprite(game))
		self.add_sprite(Fireball(game))


	def update(self):
		"""
		Updates all sprites in the game.
		"""
		[sprite.update() for sprite in self.sprites_list]


	def add_sprite(self, sprite):
		"""
		Adds a sprite to the handler.
		:param sprite: The sprite to add.
		"""
		self.sprites_list.append(sprite)
