import math

def distance(ax, bx, ay, by) -> float:
	"""
	Returns the distance between two points.
	"""
	return math.sqrt(((ax - bx) ** 2) + ((ay - by) ** 2))