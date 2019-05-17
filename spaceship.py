import pygame
from typing import List, Tuple, Optional
from math import sin, cos, pi, atan, atan2, hypot

cell_size = 10


class SpaceObject:
    """A object composed of cells on the game map
    body:
        Components of the starship
    position:
        xy coordinates of the top left of the starship body
    hit_check_range:
        How close to this object's position a bullet must be to check for a hit
    rotation:
        current rotation of the object in radians
    """
    body: List[List[int]]
    position: Tuple[float, float]
    hit_check_range: int
    rotation: float
    velocity_x: float
    velocity_y: float

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int]) -> None:
        self.name = name
        self.body = body
        self.hit_check_range = int(hypot(len(body), len(body[0])) * cell_size // 2)
        self.faction = faction
        self.position = position
        self.rotation = 0
        self.velocity_x = 0
        self.velocity_y = 0

    def ship_to_true(self, point: Tuple[int, int]) -> Tuple[int, int]:
        x = int(point[0] * cos(self.rotation) - point[1] * sin(self.rotation) + self.position[0])
        y = int(point[1] * cos(self.rotation) + point[0] * sin(self.rotation) + self.position[1])
        return x, y

    def update(self):
        self.rotation = self.rotation % (2 * pi)
        self.position = self.position[0] + self.velocity_x, self.position[1] + self.velocity_y


class StarShip(SpaceObject):
    """A starship on the game map
    acceleration:
        This starship's acceleration
    turn_speed:
        This starship's turn speed
    destination:
        Point the starship is moving towards
    selected:
        If this ship is currently selected by the player
    max_speed:
        Highest velocity the ship can have
    """
    acceleration: float
    turn_speed: float
    destination: Optional[Tuple[int, int]]
    selected: bool
    max_speed: float

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int],
                 acceleration: float, turn_speed: float, max_speed: float) -> None:
        SpaceObject.__init__(self, name, body, faction, position)
        self.acceleration = acceleration
        self.turn_speed = turn_speed
        self.destination = None
        self.selected = False
        self.max_speed = max_speed

    def update(self) -> None:
        if self.destination is not None:
            self.move_to()
            if hypot(self.destination[0] - self.position[0], self.destination[1] - self.position[1]) \
                    < self.hit_check_range:
                self.destination = None
        elif self.velocity_x != 0 or self.velocity_y != 0:
            velocity_angle = atan2(self.velocity_y, self.velocity_x)
            if self.velocity_x != 0:
                if self.velocity_x > 0:
                    self.velocity_x -= min(0.02*cos(velocity_angle), self.velocity_x)
                else:
                    self.velocity_x -= max(0.02 * cos(velocity_angle), self.velocity_x)
            if self.velocity_y != 0:
                if self.velocity_y > 0:
                    self.velocity_y -= min(0.02*sin(velocity_angle), self.velocity_y)
                else:
                    self.velocity_y -= max(0.02 * sin(velocity_angle), self.velocity_y)
        SpaceObject.update(self)

    def move_to(self) -> None:
        x = self.destination[0] - self.position[0]
        y = self.destination[1] - self.position[1]
        destination_angle = atan2(y, x)
        if destination_angle < 0:
            destination_angle += (2*pi)
        difference_in_angles = destination_angle - self.rotation
        if difference_in_angles != 0:
            if abs(difference_in_angles) < self.turn_speed or abs(difference_in_angles) > 2*pi - self.turn_speed:
                self.rotation = destination_angle
            else:
                if abs(difference_in_angles) < pi:
                    if difference_in_angles < 0:
                        self.rotation -= self.turn_speed
                    else:
                        self.rotation += self.turn_speed
                else:
                    if difference_in_angles < 0:
                        self.rotation += self.turn_speed
                    else:
                        self.rotation -= self.turn_speed

        self.velocity_x += self.acceleration * cos(self.rotation)
        self.velocity_y += self.acceleration * sin(self.rotation)

        if hypot(self.velocity_x, self.velocity_y) > self.max_speed:
            velocity_angle = atan2(self.velocity_y, self.velocity_x)
            self.velocity_x = self.max_speed * cos(velocity_angle)
            self.velocity_y = self.max_speed * sin(velocity_angle)
