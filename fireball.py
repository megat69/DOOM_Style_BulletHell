from sprite_object import SpriteObject
from utils import distance


class Fireball(SpriteObject):
	def __init__(
			self,
			game,
			path: str = 'assets/sprites/fireball.png',
			pos: tuple = (10.5, 4.5),
			scale: float = 0.25,
			shift: int = 0.5
	):
		super().__init__(game, path, pos, scale, shift)
		# Lowers the culling distance a ton so the player can still see the fireball even if really close by
		self.culling_distance = 0.1

	def update(self):
		"""
		Called every frame : If the player is colliding with the projectile, we lower their health.
		"""
		super().update()

		# Finds the distance between the projectile and the player
		if distance(self.game.player.x, self.x, self.game.player.y, self.y) < self.culling_distance:
			# Lowers the player health
			self.game.player.health -= 1
			self.game.player.check_health()
			# Removes the projectile from the list of sprites
			self.game.objects_handler.sprites_list.remove(self)
