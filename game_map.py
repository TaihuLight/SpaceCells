import pygame
from typing import Tuple, List
from spaceship import StarShip
from math import hypot


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
        how zoomed in the screen is
    space_objects:
        all space objects on the map
    player_ships:
        all ships controlled by the player
    selected_ships:
        all ships currently selected by the player
    """
    width: int
    height: int
    size: int
    x_offset: int
    y_offset: int
    zoom: int
    space_objects: List
    player_ships: List[StarShip]
    selected_ships: List[StarShip]

    def __init__(self, size: int, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.size = size
        self.x_offset = 0
        self.y_offset = 0
        self.zoom = 1
        self.space_objects = []
        self.player_ships = []
        self.selected_ships = []

        self.create_space_object('corvette', (500, 500))
        self.create_space_object('corvette', (300, 600))
        self.create_space_object('corvette', (700, 809))

    def pan(self, motion: Tuple[int, int]) -> None:
        self.x_offset += motion[0]//self.zoom
        self.y_offset += motion[1]//self.zoom

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

    def check_selection_click(self, clicked_mouse_position: Tuple[int, int]):
        for ship in self.player_ships:
            if hypot(clicked_mouse_position[0] - ship.position[0], clicked_mouse_position[1] - ship.position[1]) \
                    < ship.hit_check_range:
                ship.selected = True
                self.selected_ships.append(ship)

    def check_selection_box(self, clicked_mouse_position: Tuple[int, int]) -> None:
        current_mouse_position = pygame.mouse.get_pos()
        current_mouse_position = self.screen_to_true(current_mouse_position)
        left_x = min(clicked_mouse_position[0], current_mouse_position[0])
        right_x = max(clicked_mouse_position[0], current_mouse_position[0])
        bottom_y = min(clicked_mouse_position[1], current_mouse_position[1])
        top_y = max(clicked_mouse_position[1], current_mouse_position[1])

        for ship in self.player_ships:
            if left_x < ship.position[0] < right_x and bottom_y < ship.position[1] < top_y:
                ship.selected = True
                self.selected_ships.append(ship)

    def unselect(self) -> None:
        for ship in self.selected_ships:
            ship.selected = False
        self.selected_ships = []

    def set_destination(self) -> None:
        true_destination = self.screen_to_true(pygame.mouse.get_pos())
        for ship in self.selected_ships:
            ship.destination = true_destination

    def create_space_object(self, name: str, position: Tuple[int, int]) -> None:
        if name == 'corvette':
            body = [[1, 1, 0, 0, 0],
                    [0, 1, 1, 1, 1],
                    [0, 1, 1, 1, 1],
                    [1, 1, 0, 0, 0]]
            new_space_object = StarShip(name, body, 'player', position, 0.01, 0.02, 1)
        self.space_objects.append(new_space_object)
        self.player_ships.append(new_space_object)
