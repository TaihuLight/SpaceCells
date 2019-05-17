import pygame
from typing import Tuple, List
from spaceship import StarShip


class GameMap:
    """Stores all objects on the game map
    width:
        width of the screen
    height:
        height of the screen
    size:
        size of the game map
    x_offset:
        offset in the x direction
    y_offset:
        offset in the y direction
    zoom:
    """
    size: int
    x_offset: int
    y_offset: int
    zoom: int
    spaceships: List

    def __init__(self, size: int, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.size = size
        self.x_offset = 0
        self.y_offset = 0
        self.zoom = 1
        self.spaceships = []
        new_starship = StarShip()
        self.spaceships.append(new_starship)

    def pan(self, motion: Tuple[int, int]) -> None:
        self.x_offset += motion[0]
        self.y_offset += motion[1]

    def change_zoom(self, i: float):
        if round(self.zoom + i) != 0.0:
            old_center = self.screen_to_true((self.width//2, self.height//2))
            self.zoom += i
            new_center = self.screen_to_true((self.width//2, self.height//2))
            self.pan((new_center[0] - old_center[0], new_center[1] - old_center[1]))

    def true_to_screen(self, point: Tuple[int, int]) -> Tuple[int, int]:
        x = round((point[0] + self.x_offset) * self.zoom)
        y = round((point[1] + self.y_offset) * self.zoom)
        return x, y

    def screen_to_true(self, point: Tuple[int, int]) -> Tuple[int, int]:
        x = round(point[0]/self.zoom - self.x_offset)
        y = round(point[1] / self.zoom - self.y_offset)
        return x, y
