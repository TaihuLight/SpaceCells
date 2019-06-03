# Commit message change
import pygame
from typing import Tuple, List, Dict
from spaceship import StarShip, Bullet, short_range, medium_range, Battleship, Miner, Asteroid
from math import hypot, atan2
from random import randint
update_target_total_time = 5
test_env = False


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
    game_factions:
        names of all the factions except neutral
    all_ships:
        all StarShip objects sorted by faction
    selected_ships:
        all ships currently selected by the player
    bullets:
        all bullets on the game map
    update_target_time:
        time until targets for all ships gets updates
    resources:
        The type and amount of the player's resources
    """
    width: int
    height: int
    size: int
    x_offset: int
    y_offset: int
    zoom: int
    space_objects: List
    game_factions: List[str]
    all_ships: Dict[str, List[StarShip]]
    selected_ships: List[StarShip]
    bullets: List[Bullet]
    update_target_time: int
    resources: Dict[str, int]

    def __init__(self, size: int, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.size = size
        self.x_offset = 0
        self.y_offset = 0
        self.zoom = 1
        self.space_objects = []
        self.game_factions = ['player', 'pirate']
        self.all_ships = {'neutral': [], 'player': [], 'pirate': []}
        self.selected_ships = []
        self.bullets = []
        self.update_target_time = update_target_total_time
        self.resources = {'alloy': 0, 'crystal': 0, 'scrap': 0}
        if test_env:
            self.create_space_object('asteroid', (700, 700))
            self.create_space_object('corvette', (500, 500))
            self.create_space_object('corvette', (300, 600))

        else:
            self.create_space_object('corvette', (500, 500))
            self.create_space_object('corvette', (300, 600))
            self.create_space_object('corvette', (600, 300))
            self.create_space_object('miner', (300, 300))
            self.create_space_object('miner', (200, 200))
            self.create_space_object('gunboat', (1500, 1500))
            self.create_space_object('gunboat', (1600, 1500))
            self.create_space_object('gunboat', (1500, 1600))
            self.create_space_object('gunboat', (1400, 100))
            self.create_space_object('gunboat', (1400, 200))
            self.create_space_object('gunboat', (1500, 100))
            self.create_space_object('hammerhead', (100, 1500))
            self.create_space_object('hammerhead', (300, 1500))
            self.create_space_object('hammerhead', (100, 1600))
            for _ in range(10):
                self.create_space_object('asteroid', (randint(0, self.size), randint(0, self.size)))

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

    def true_to_screen_float(self, point: Tuple[int, int]) -> Tuple[float, float]:
        x = (point[0] + self.x_offset) * self.zoom
        y = (point[1] + self.y_offset) * self.zoom
        return x, y

    def screen_to_true(self, point: Tuple[int, int]) -> Tuple[int, int]:
        x = round(point[0]/self.zoom - self.x_offset)
        y = round(point[1] / self.zoom - self.y_offset)
        return x, y

    def check_selection_click(self, clicked_mouse_position: Tuple[int, int]) -> None:
        for ship in self.all_ships['player']:
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

        for ship in self.all_ships['player']:
            if left_x < ship.position[0] < right_x and bottom_y < ship.position[1] < top_y:
                ship.selected = True
                self.selected_ships.append(ship)

    def unselect(self) -> None:
        for ship in self.selected_ships:
            ship.selected = False
        self.selected_ships = []

    def handel_order(self) -> None:
        if self.selected_ships:
            true_mouse_position = self.screen_to_true(pygame.mouse.get_pos())
            for space_object in self.space_objects:
                if space_object.faction != 'player':
                    if hypot(true_mouse_position[0] - space_object.position[0],
                             true_mouse_position[1] - space_object.position[1]) < space_object.hit_check_range:
                        if space_object.faction == 'neutral':
                            for selected_ship in self.selected_ships:
                                if isinstance(selected_ship, Miner):
                                    selected_ship.set_target(space_object)
                        else:
                            for selected_ship in self.selected_ships:
                                if not isinstance(selected_ship, Miner):
                                    selected_ship.set_target(space_object)
                        return

            # Only run if no enemy ship selected
            self.set_destination(true_mouse_position)

    def set_destination(self, true_destination: Tuple[int, int]) -> None:
        amount_selected = len(self.selected_ships)
        if amount_selected > 1:
            mid_position_x = 0
            mid_position_y = 0
            for ship in self.selected_ships:
                mid_position_x += ship.position[0]
                mid_position_y += ship.position[1]
            mid_position_x = mid_position_x / amount_selected
            mid_position_y = mid_position_y / amount_selected
            for ship in self.selected_ships:
                ship.set_destination((true_destination[0] + ship.position[0] - mid_position_x,
                                      true_destination[1] + ship.position[1] - mid_position_y))
        elif amount_selected == 1:
            self.selected_ships[0].set_destination(true_destination)

    def update(self) -> None:
        self.update_target_time -= 1
        if self.update_target_time == 0:
            self.update_targets()
            self.update_target_time = update_target_total_time

        for bullet in self.bullets:
            bullet.update()
            if bullet.lifetime == 0:
                self.bullets.remove(bullet)

        self.check_collisions()

        for space_object in self.space_objects:
            space_object.update(self.bullets)

            # Check if ships have been disabled
            if space_object.hull is not None and space_object.hull <= 0:
                if space_object.faction == 'player':
                    self.all_ships['player'].remove(space_object)
                    if space_object in self.selected_ships:
                        self.selected_ships.remove(space_object)
                else:
                    self.all_ships[space_object.faction].remove(space_object)
                space_object.deactivate()
                self.all_ships['neutral'].append(space_object)

            # Remove objects that have no cells
            if space_object.faction == 'neutral' and space_object.cells <= 0:
                self.space_objects.remove(space_object)
                if space_object in self.all_ships:
                    self.all_ships['neutral'].remove(space_object)

    def update_targets(self):
        for faction in self.all_ships:
            for ship in self.all_ships[faction]:
                ship.close_targets = []
                ship.medium_targets = []
                ship.close_ships = {}

        for i in range(len(self.game_factions)):
            for j in range(i + 1, len(self.game_factions)):
                for ship1 in self.all_ships[self.game_factions[i]]:
                    for ship2 in self.all_ships[self.game_factions[j]]:
                        x = ship2.position[0] - ship1.position[0]
                        y = ship2.position[1] - ship1.position[1]
                        distance = hypot(x, y)
                        if distance < short_range:
                            if ship1.faction != 'neutral':
                                ship1.close_targets.append((atan2(y, x)))
                            if ship2.faction != 'neutral':
                                ship2.close_targets.append((atan2(-y, -x)))
                        if distance < medium_range:
                            if ship1.faction != 'neutral':
                                ship1.medium_targets.append((atan2(y, x)))
                                ship1.close_ships[distance] = ship2
                            if ship2.faction != 'neutral':
                                ship2.medium_targets.append((atan2(-y, -x)))
                                ship2.close_ships[distance] = ship1

    def check_collisions(self) -> None:
        for i, object1 in enumerate(self.space_objects[:len(self.space_objects) - 1]):
            for object2 in self.space_objects[i + 1:]:
                if object1.faction == 'neutral' or object1.faction != object2.faction:
                    x = object2.position[0] - object1.position[0]
                    y = object2.position[1] - object1.position[1]
                    distance = hypot(x, y)
                    if distance < object1.hit_check_range + object2.hit_check_range:
                        object1.handel_collision(object2)

    def create_space_object(self, name: str, position: Tuple[int, int]) -> None:
        if name == 'corvette':
            body = [[2, 2, 2, 2, 0, 0, 0, 0, 0, 0],
                    [2, 1, 1, 2, 2, 2, 2, 4, 0, 0],
                    [0, 0, 1, 1, 3, 1, 1, 1, 2, 0],
                    [0, 0, 0, 1, 1, 1, 1, 1, 3, 2],
                    [0, 0, 1, 1, 3, 1, 1, 1, 2, 0],
                    [2, 1, 1, 2, 2, 2, 2, 4, 0, 0],
                    [2, 2, 2, 2, 0, 0, 0, 0, 0, 0]]
            new_space_object = Battleship(name, body, 'player', position, 0.01, 0.01, 0.5)
            self.all_ships['player'].append(new_space_object)
        elif name == 'miner':
            body = [[2, 2, 2, 0, 0, 0],
                    [0, 2, 2, 2, 2, 2],
                    [0, 0, 2, 2, 3, 2],
                    [0, 2, 2, 2, 2, 2],
                    [2, 2, 2, 0, 0, 0]]
            new_space_object = Miner(name, body, 'player', position, 0.01, 0.05, 1, self.resources)
            self.all_ships['player'].append(new_space_object)
        elif name == 'gunboat':
            body = [[0, 2, 0, 2, 2, 2, 0],
                    [2, 1, 2, 1, 1, 1, 2],
                    [2, 3, 1, 1, 3, 1, 2],
                    [2, 1, 2, 1, 1, 1, 2],
                    [0, 2, 0, 2, 2, 2, 0]]
            new_space_object = Battleship(name, body, 'pirate', position, 0.01, 0.01, 0.5)
            self.all_ships['pirate'].append(new_space_object)
        elif name == 'hammerhead':
            body = [[2, 2, 2, 0, 0, 0, 0, 0, 2, 2],
                    [1, 1, 1, 2, 0, 0, 0, 0, 2, 4],
                    [0, 0, 0, 1, 1, 2, 2, 2, 1, 2],
                    [0, 0, 0, 1, 1, 1, 1, 1, 1, 4],
                    [0, 0, 0, 1, 1, 2, 2, 2, 1, 2],
                    [1, 1, 1, 2, 0, 0, 0, 0, 2, 4],
                    [2, 2, 2, 0, 0, 0, 0, 0, 2, 2]]
            new_space_object = Battleship(name, body, 'pirate', position, 0.01, 0.01, 0.5)
            self.all_ships['pirate'].append(new_space_object)
        elif name == 'asteroid':
            body = []
            size = 11
            middle = size // 2

            left_extend = 0
            right_extend = 0
            for i in range(size):
                row = []
                if i < middle:
                    if left_extend < (size - 1)//2:
                        left_extend += randint(0, 2)
                    if right_extend < (size - 1)//2:
                        right_extend += randint(0, 2)
                else:
                    if 0 < left_extend:
                        left_extend -= randint(0, 2)
                    if 0 < right_extend:
                        right_extend -= randint(0, 2)
                for k in range(size):
                    if middle - left_extend <= k <= middle + right_extend:
                        row.append(randint(1, 2))
                    else:
                        row.append(0)
                body.append(row)
            new_space_object = Asteroid(name, body, 'neutral', position, 'alloy')
        self.space_objects.append(new_space_object)
