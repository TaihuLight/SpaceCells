import pygame
from typing import List, Tuple
from math import sin, cos


class SpaceObject:
    """A object composed of cells on the game map
    body:
        Components of the starship
    position:
        xy coordinates of the top left of the starship body
    rotation:
        current rotation of the object in radians
    """
    body: List[List[int]]
    position: Tuple[int, int]
    rotation: float

    def __init__(self) -> None:
        self.body = [[0, 0, 1, 0, 0],
                     [0, 1, 1, 1, 0],
                     [0, 1, 1, 1, 0],
                     [0, 1, 0, 1, 0]]
        self.position = (500, 500)
        self.rotation = 1

    def ship_to_true(self, point: Tuple[int, int]) -> Tuple[int, int]:
        x = int(point[0] * cos(self.rotation) - point[1] * sin(self.rotation) + self.position[0])
        y = int(point[1] * cos(self.rotation) + point[0] * sin(self.rotation) + self.position[1])
        return x, y


class StarShip(SpaceObject):
    """A starship on the game map

    """
    def __init__(self) -> None:
        SpaceObject.__init__(self)
