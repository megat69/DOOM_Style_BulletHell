import pygame


def portal_appear(game) -> bool:
	"""
	Makes the portal appear once all enemies were killed.
	"""
	return (
		len([entity for entity in game.objects_handler.entities if entity.alive]) == 0
	) and (
		len(game.weapons) > 1
	)


FUNCTIONS = {
	"portal_appear": portal_appear
}
