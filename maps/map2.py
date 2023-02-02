import pygame


def portal_appear(game) -> bool:
	"""
	Makes the portal appear once all enemies were killed.
	"""
	return len([enemy for enemy in game.objects_handler.entities if enemy.alive]) == 0


FUNCTIONS = {
	"portal_appear": portal_appear
}
