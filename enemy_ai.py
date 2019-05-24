from game_map import GameMap
from spaceship import StarShip
from typing import List
from random import choice, randint


class PodManager:
    """Manages a group of StarShips
    target:
        Faction this pod is attacking
    change_target_cooldown:
        Time until target can be updated
    star_ships:
        StarShips in this pod
    faction:
        This pod's faction
    game_map:
        stores all objects on the game map
    """
    target: str
    change_target_cooldown: int
    star_ships: List[StarShip]
    faction: str
    game_map: GameMap

    def __init__(self, game_map: GameMap, star_ships: List[StarShip]) -> None:
        self.target = None
        self.change_target_cooldown = 0
        self.star_ships = star_ships
        self.faction = self.star_ships[0].faction
        self.game_map = game_map

    def update(self) -> None:
        to_remove = []
        for ship in self.star_ships:
            if ship.faction != self.faction:
                to_remove.append(ship)
        for ship in to_remove:
            self.star_ships.remove(ship)

        if self.change_target_cooldown > 0:
            self.change_target_cooldown -= 1
        if self.change_target_cooldown == 0:
            target_found = False
            for ship in self.star_ships:
                if ship.close_ships:
                    close_ships = list(ship.close_ships.values())
                    self.target = choice(close_ships).faction
                    self.change_target_cooldown = 5
                    target_found = True
                    break
            if not target_found:
                self.target = None

        if self.target is None:
            if all(ship.destination is None for ship in self.star_ships):
                new_destination_x = randint(50, self.game_map.size-50)
                new_destination_y = randint(50, self.game_map.size-50)
                for ship in self.star_ships:
                    x = randint(-200, 200)
                    y = randint(-200, 200)
                    ship.destination = new_destination_x + x, new_destination_y + y
        else:
            pass

