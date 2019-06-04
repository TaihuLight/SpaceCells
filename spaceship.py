# Commit message change
from __future__ import annotations
from typing import List, Tuple, Optional, Dict
from math import sin, cos, pi, atan2, hypot
from random import randint


cell_size = 10
short_range = 500
medium_range = 800
turret_cooldown = 160
total_cannon_cooldown = 160
bullet_speed = 2


class SpaceObject:
    """A object composed of cells on the game map
    name:
        This objects's type
    body:
        Components of the starship
    faction:
        Faction this object belongs to
    position:
        true x, y coordinates of the center of the starship body
    hit_check_range:
        How close to this object's position a bullet must be to check for a hit
    faction:
        Faction this ship belongs to
    rotation:
        current rotation of the object in radians
    hull:
        Health of the space object
    cells:
        Number of non zero cells in body
    """
    name: str
    body: List[List[int]]
    position: Tuple[float, float]
    hit_check_range: int
    faction: str
    rotation: float
    velocity_x: float
    velocity_y: float
    hull: Optional[int]
    cells: int

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int]) -> None:
        self.name = name
        self.body = body
        self.hit_check_range = int(hypot(len(body), len(body[0])) * cell_size // 2)
        self.faction = faction
        self.position = position
        self.rotation = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.hull = None
        self.cells = 0
        for sublist in self.body:
            for number in sublist:
                if number != 0:
                    self.cells += 1

    def update(self, bullets: List[Bullet]) -> None:
        raise NotImplementedError

    def ship_to_true(self, point: Tuple[int, int]) -> Tuple[float, float]:
        x = point[0] * cos(self.rotation) - point[1] * sin(self.rotation) + int(self.position[0])
        y = point[1] * cos(self.rotation) + point[0] * sin(self.rotation) + int(self.position[1])
        return x, y

    def true_to_ship(self, point: Tuple[int, int]) -> Tuple[int, int]:
        x = int((point[0] - self.position[0]) * cos(-self.rotation) - (point[1] - self.position[1]) * sin(-self.rotation))
        y = int((point[1] - self.position[1]) * cos(-self.rotation) + (point[0] - self.position[0]) * sin(-self.rotation))
        return x, y

    def true_to_ship_float(self, point: Tuple[float, float]) -> Tuple[float, float]:
        x = (point[0] - self.position[0]) * cos(-self.rotation) - (point[1] - self.position[1]) * sin(-self.rotation)
        y = (point[1] - self.position[1]) * cos(-self.rotation) + (point[0] - self.position[0]) * sin(-self.rotation)
        return x, y

    def body_to_ship(self, position: Tuple[int, int]) -> Tuple[int, int]:
        x = position[0]
        y = position[1]
        top_left_point = cell_size * (-len(self.body[0]) / 2) + cell_size // 2, \
                         cell_size * (-len(self.body) / 2) + cell_size // 2
        new_x = top_left_point[0] + cell_size * x
        new_y = top_left_point[1] + cell_size * y
        return new_x, new_y

    def update_position(self):
        self.rotation = self.rotation % (2 * pi)
        self.position = self.position[0] + self.velocity_x, self.position[1] + self.velocity_y

    def check_damage_from_bullets(self, bullets: List[Bullet]) -> None:
        for bullet in bullets:
            if bullet.faction != self.faction and hypot(bullet.position[0] - self.position[0],
                                                        bullet.position[1] - self.position[1]) < self.hit_check_range:
                ship_bullet_position = self.true_to_ship(bullet.position)
                x = (ship_bullet_position[0] + int(len(self.body[0]) / 2 * cell_size)) // cell_size
                y = (ship_bullet_position[1] + int(len(self.body) / 2 * cell_size)) // cell_size
                if self.handel_damage(x, y, bullet.damage):
                    bullets.remove(bullet)

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
        raise NotImplementedError

    def handel_mine(self, x: int, y: int, player_resources: Dict[str, int]) -> None:
        raise NotImplementedError

    def handel_collision(self, object2: SpaceObject):
        top_left_point = cell_size * (-len(self.body[0]) / 2) + cell_size//2, \
                         cell_size * (-len(self.body) / 2) + cell_size//2
        top_second_left_point = cell_size * (-len(self.body[0]) / 2) + cell_size + cell_size // 2, \
                                cell_size * (-len(self.body) / 2) + cell_size // 2
        point1 = object2.true_to_ship_float(self.ship_to_true(top_left_point))
        point2 = object2.true_to_ship_float(self.ship_to_true(top_second_left_point))
        x_difference = point2[0] - point1[0]
        y_difference = point2[1] - point1[1]
        for y in range(len(self.body)):
            for x in range(len(self.body[y])):
                if self.body[y][x] != 0:
                    base_point_x = point1[0] + x_difference * x - y_difference * y
                    base_point_y = point1[1] + y_difference * x + x_difference * y
                    object2_x = int((base_point_x + len(object2.body[0]) / 2 * cell_size) / cell_size)
                    object2_y = int((base_point_y + len(object2.body) / 2 * cell_size) / cell_size)
                    if object2.handel_damage(object2_x, object2_y, 2):
                        self.handel_damage(x, y, 2)


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
    close_targets:
        A list of angles between this ship and enemy ships in close range
    medium_targets:
        A list of angles between this ship and enemy ships in medium range
    selected_target:
        Enemy ship that is being targeted by this ship
    close_ships:
        A dictionary where keys are distances and values are enemy ships
    repair_cost:
        Type and amount of resources required to repair this ship
    repair_stack:
        Stack of the positions, type, and required resource of this ship's destroyed cells
    """
    acceleration: float
    turn_speed: float
    destination: Optional[Tuple[float, float]]
    selected: bool
    max_speed: float
    close_targets: List[float]
    medium_targets: List[float]
    selected_target: Optional[SpaceObject]
    close_ships: Dict[float, StarShip]
    repair_stack: List[Tuple[int, int, int, str]]
    repair_cost: Dict[str, int]

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int],
                 acceleration: float, turn_speed: float, max_speed: float) -> None:
        SpaceObject.__init__(self, name, body, faction, position)
        self.hull = 0
        self.acceleration = acceleration
        self.turn_speed = turn_speed
        self.destination = None
        self.selected = False
        self.max_speed = max_speed
        self.close_targets = []
        self.medium_targets = []
        self.selected_target = None
        self.close_ships = {}
        self.set_hull()
        self.repair_stack = []
        self.repair_cost = {'alloy': 0, 'crystal': 0}

    def set_hull(self) -> None:
        raise NotImplementedError

    def update(self, bullets: List[Bullet]) -> None:
        if self.destination is not None:
            self.move_to(self.destination)
            if hypot(self.destination[0] - self.position[0], self.destination[1] - self.position[1]) \
                    < self.hit_check_range:
                self.destination = None
        elif self.selected_target is not None:
            self.handel_target()
        else:
            self.decelerate()

    def set_destination(self, destination: Tuple[float, float]) -> None:
        self.destination = destination
        self.selected_target = None

    def set_target(self, target: SpaceObject) -> None:
        self.selected_target = target
        self.destination = None

    def move_to(self, destination: Tuple[float, float]) -> None:
        self.rotate_towards(destination)

        self.velocity_x += self.acceleration * cos(self.rotation)
        self.velocity_y += self.acceleration * sin(self.rotation)

        if hypot(self.velocity_x, self.velocity_y) > self.max_speed:
            velocity_angle = atan2(self.velocity_y, self.velocity_x)
            self.velocity_x = self.max_speed * cos(velocity_angle)
            self.velocity_y = self.max_speed * sin(velocity_angle)

    def handel_target(self) -> None:
        raise NotImplementedError

    def rotate_towards(self, destination: Tuple[float, float]) -> None:
        x = destination[0] - self.position[0]
        y = destination[1] - self.position[1]
        destination_angle = atan2(y, x)
        if destination_angle < 0:
            destination_angle += (2 * pi)
        difference_in_angles = destination_angle - self.rotation
        if difference_in_angles != 0:
            if abs(difference_in_angles) < self.turn_speed or abs(difference_in_angles) > 2 * pi - self.turn_speed:
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

    def decelerate(self) -> None:
        if self.velocity_x != 0 or self.velocity_y != 0:
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

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
        raise NotImplementedError

    def handel_mine(self, x: int, y: int, player_resources: Dict[str, int]) -> None:
        if self.handel_damage(x, y, 2):
            player_resources['scrap'] += 1

    def handel_repair(self, x: int, y: int, cell_number: int) -> None:
        raise NotImplementedError

    def deactivate(self) -> None:
        self.faction = 'neutral'
        self.destination = None
        self.selected_target = None
        self.hull = None
        self.selected = False
        self.close_targets = []
        self.medium_targets = []
        self.close_ships = {}


class Battleship(StarShip):
    """A battleship class ship with turrets and cannons
    turrets:
        Location of all turrets in the body array
    cannons:
        Location of all cannons in the body array
    cannon_cooldown:
        How many ticks until the cannons can fire again
    """
    turrets: Dict[Tuple[int, int], int]
    cannons: List[Tuple[int, int]]
    cannon_cooldown: int

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int],
                 acceleration: float, turn_speed: float, max_speed: float):
        self.turrets = {}
        self.cannons = []
        self.cannon_cooldown = total_cannon_cooldown
        StarShip.__init__(self, name, body, faction, position, acceleration, turn_speed, max_speed)

    def set_hull(self) -> None:
        for i, sublist in enumerate(self.body):
            for j, number in enumerate(sublist):
                if number == 1 or number == 2:
                    self.hull += 1
                elif number == 3:
                    self.turrets[j, i] = randint(0, turret_cooldown)
                    self.hull += 1
                elif number == 4:
                    self.cannons.append((j, i))
                    self.hull += 1

        self.hull = self.hull // 3

    def update(self, bullets: List[Bullet]) -> None:
        StarShip.update(self, bullets)

        # Update this ship's turrets
        if self.close_targets:
            for turret_pos in self.turrets:
                self.turrets[turret_pos] -= 1
                if self.turrets[turret_pos] == 0:
                    position = self.ship_to_true(
                        (int(cell_size * (turret_pos[0] - len(self.body[0]) / 2) + cell_size // 2),
                         int(cell_size * (turret_pos[1] - len(self.body) / 2) + cell_size // 2)))
                    rotation = self.close_targets[randint(0, len(self.close_targets) - 1)]
                    new_bullet = Bullet(position, rotation, self.faction, 1)
                    bullets.append(new_bullet)
                    self.turrets[turret_pos] = turret_cooldown

        # Update this ship's cannons
        if self.cannon_cooldown > 0:
            self.cannon_cooldown -= 1
        cannons_fire = False
        if self.cannon_cooldown == 0:
            for target_angle in self.medium_targets:
                if target_angle < 0:
                    target_angle += (2 * pi)
                difference_in_angles = target_angle - self.rotation
                if difference_in_angles == 0 or abs(difference_in_angles) < 0.209 or \
                        abs(difference_in_angles) > 2 * pi - 0.209:
                    cannons_fire = True
                    break

        if cannons_fire:
            for cannon_pos in self.cannons:
                position = self.ship_to_true(
                    (int(cell_size * (cannon_pos[0] - len(self.body[0]) / 2) + cell_size // 2),
                     int(cell_size * (cannon_pos[1] - len(self.body) / 2) + cell_size // 2)))
                rotation = self.rotation
                new_bullet = Bullet(position, rotation, self.faction, 2)
                bullets.append(new_bullet)
            self.cannon_cooldown = total_cannon_cooldown

        SpaceObject.update_position(self)
        self.check_damage_from_bullets(bullets)

    def handel_target(self) -> None:
        if self.selected_target.faction == 'neutral' or self.selected_target.faction == self.faction:
            self.selected_target = None
        else:
            target_distance = hypot(self.selected_target.position[0] - self.position[0],
                                    self.selected_target.position[1] - self.position[1])
            if len(self.cannons) > 0 and target_distance < medium_range:
                self.rotate_towards(self.selected_target.position)
                self.decelerate()
            elif target_distance < short_range:
                self.decelerate()
            else:
                self.move_to(self.selected_target.position)

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
        if 0 <= y < len(self.body) and 0 <= x < len(self.body[0]):
            if self.body[y][x] == 0:
                return False
            elif self.body[y][x] == 1:
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                self.repair_stack.append((x, y, 1, 'alloy'))
                self.repair_cost['alloy'] += 1
                return True
            elif self.body[y][x] == 2:
                if damage == 1:
                    self.body[y][x] = 1
                    self.repair_stack.append((x, y, 2, 'alloy'))
                    self.repair_cost['alloy'] += 1
                    return True
                elif damage == 2:
                    self.body[y][x] = 0
                    if self.hull is not None:
                        self.hull -= 1
                    self.cells -= 1
                    self.repair_stack.append((x, y, 2, 'alloy'))
                    self.repair_stack.append((x, y, 1, 'alloy'))
                    self.repair_cost['alloy'] += 2
                    return True
            elif self.body[y][x] == 3:
                del self.turrets[(x, y)]
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                self.repair_stack.append((x, y, 3, 'crystal'))
                self.repair_cost['crystal'] += 1
                return True
            elif self.body[y][x] == 4:
                self.cannons.remove((x, y))
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                self.repair_stack.append((x, y, 4, 'crystal'))
                self.repair_cost['crystal'] += 1
                return True
        return False

    def handel_repair(self, x: int, y: int, cell_number: int) -> None:
        if cell_number == 1:
            self.body[y][x] = 1
            self.hull += 1
            self.cells += 1
            self.repair_cost['alloy'] -= 1
        elif cell_number == 2:
            self.body[y][x] = 2
            self.repair_cost['alloy'] -= 1
        elif cell_number == 3:
            self.body[y][x] = 3
            self.turrets[x, y] = 0
            self.hull += 1
            self.cells += 1
            self.repair_cost['crystal'] -= 1
        elif cell_number == 4:
            self.body[y][x] = 4
            self.cannons.append((x, y))
            self.hull += 1
            self.cells += 1
            self.repair_cost['crystal'] -= 1


class Miner(StarShip):
    """Worker ship that can mine and salvage
    drill:
        Location of the drill in the body array
    mining_charge:
        Charge of the drill
    target_cell:
        Location of the cell being mined in selected target's body
    player_resources:
        The type and amount of the player's resources
    """
    drill: Optional[Tuple[int, int]]
    mining_charge: int
    target_cell: Optional[Tuple[int, int]]
    player_resources: Dict[str, int]

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int],
                 acceleration: float, turn_speed: float, max_speed: float, resources: Dict[str, int]):
        self.mining_charge = 0
        self.target_cell = None
        self.player_resources = resources
        StarShip.__init__(self, name, body, faction, position, acceleration, turn_speed, max_speed)

    def set_hull(self) -> None:
        for i, sublist in enumerate(self.body):
            for j, number in enumerate(sublist):
                if number == 1 or number == 2:
                    self.hull += 1
                elif number == 3:
                    self.drill = j, i
                    self.hull += 1

        self.hull = self.hull // 3

    def update(self, bullets: List[Bullet]) -> None:
        StarShip.update(self, bullets)

        SpaceObject.update_position(self)
        self.check_damage_from_bullets(bullets)

    def set_destination(self, destination: Tuple[float, float]) -> None:
        StarShip.set_destination(self, destination)
        self.mining_charge = 0
        self.target_cell = None

    def set_target(self, target: SpaceObject) -> None:
        StarShip.set_target(self, target)
        self.mining_charge = 0
        self.target_cell = None

    def handel_target(self) -> None:
        if self.selected_target.cells <= 0:
            self.selected_target = None
            self.target_cell = None
            self.mining_charge = 0
        else:
            target_distance = hypot(self.selected_target.position[0] - self.position[0],
                                    self.selected_target.position[1] - self.position[1])
            if target_distance < self.hit_check_range + self.selected_target.hit_check_range + 30:
                self.rotate_towards(self.selected_target.position)
                self.decelerate()
                if self.drill is not None:
                    if self.selected_target.faction == 'neutral':
                        self.mine()
                    elif self.selected_target.faction == 'player':
                        self.repair()
            else:
                self.target_cell = None
                self.move_to(self.selected_target.position)

    def mine(self) -> None:
        if self.target_cell and self.selected_target.body[self.target_cell[1]][self.target_cell[0]] != 0:
            self.mining_charge += 1
            if self.mining_charge >= 60:
                self.selected_target.handel_mine(self.target_cell[0], self.target_cell[1], self.player_resources)
                self.target_cell = None
                self.mining_charge = 0
        else:
            for y in range(len(self.selected_target.body)):
                for x in range(len(self.selected_target.body[y])):
                    if self.selected_target.body[y][x] != 0:
                        self.target_cell = x, y
                        return

    def repair(self) -> None:
        repair_stack = self.selected_target.repair_stack
        if repair_stack:
            current_index = len(repair_stack) - 1
            while current_index >= 0:
                repair_order = repair_stack[current_index]
                if self.player_resources[repair_order[3]] > 0:
                    self.target_cell = repair_order[0], repair_order[1]
                    self.mining_charge += 1
                    if self.mining_charge >= 60:
                        self.selected_target.handel_repair(repair_order[0], repair_order[1], repair_order[2])
                        repair_stack.pop(current_index)
                        self.player_resources[repair_order[3]] -= 1
                        self.target_cell = None
                        self.mining_charge = 0
                    return
                current_index -= 1
            self.target_cell = None
        else:
            self.target_cell = None

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
        if 0 <= y < len(self.body) and 0 <= x < len(self.body[0]):
            if self.body[y][x] == 0:
                return False
            elif self.body[y][x] == 1:
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                self.repair_stack.append((x, y, 1, 'alloy'))
                self.repair_cost['alloy'] += 1
                return True
            elif self.body[y][x] == 2:
                if damage == 1:
                    self.body[y][x] = 1
                    self.repair_stack.append((x, y, 2, 'alloy'))
                    self.repair_cost['alloy'] += 1
                    return True
                elif damage == 2:
                    self.body[y][x] = 0
                    if self.hull is not None:
                        self.hull -= 1
                    self.cells -= 1
                    self.repair_stack.append((x, y, 2, 'alloy'))
                    self.repair_stack.append((x, y, 1, 'alloy'))
                    self.repair_cost['alloy'] += 2
                    return True
            elif self.body[y][x] == 3:
                self.mining_charge = 0
                self.drill = None
                self.mining_charge = 0
                self.target_cell = None
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                self.repair_stack.append((x, y, 3, 'crystal'))
                self.repair_cost['crystal'] += 1
                return True
        return False

    def handel_repair(self, x: int, y: int, cell_number: int) -> None:
        if cell_number == 1:
            self.body[y][x] = 1
            self.hull += 1
            self.cells += 1
            self.repair_cost['alloy'] -= 1
        elif cell_number == 2:
            self.body[y][x] = 2
            self.repair_cost['alloy'] -= 1
        elif cell_number == 3:
            self.body[y][x] = 3
            self.drill = (x, y)
            self.hull += 1
            self.cells += 1
            self.repair_cost['crystal'] -= 1

    def deactivate(self) -> None:
        StarShip.deactivate(self)
        self.mining_charge = 0
        self.target_cell = None


class Asteroid (SpaceObject):
    """A mineable asteroid
    resource:
        Resources obtained when this asteroid is mined
    """
    resource: str

    def __init__(self, name: str, body: List[List[int]], faction: str,
                 position: Tuple[int, int], resource: str) -> None:
        SpaceObject.__init__(self, name, body, faction, position)
        self.rotation = randint(0, 628) / 100
        self.resource = resource

    def update(self, bullets: List[Bullet]) -> None:
        self.check_damage_from_bullets(bullets)
        self.rotation += 0.001
        SpaceObject.update_position(self)

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
        if 0 <= y < len(self.body) and 0 <= x < len(self.body[0]):
            if self.body[y][x] == 1 or self.body[y][x] == 2:
                self.body[y][x] = 0
                self.cells -= 1
                return True
        return False

    def handel_mine(self, x: int, y: int, player_resources: Dict[str, int]) -> None:
        if self.body[y][x] == 2:
            player_resources[self.resource] += 1
        self.handel_damage(x, y, 2)


class Bullet:
    """A bullet fired by a turret on a starship
    position:
        true x, y coordinates of the bullet
    velocity_x:
        velocity in the x direction
    velocity_y:
        velocity in the y direction
    lifetime:
        how long until this bullet is deleted
    faction:
        faction this bullet belongs to
    """
    position: Tuple[float, float]
    velocity_x: float
    velocity_y: float
    faction: str
    lifetime: int
    damage: int

    def __init__(self, position: Tuple[float, float], rotation: float, faction: str, damage: int) -> None:
        self.position = position
        self.velocity_x = bullet_speed * cos(rotation)
        self.velocity_y = bullet_speed * sin(rotation)
        self.faction = faction
        self.damage = damage
        if damage == 1:
            self.lifetime = 250
        elif damage == 2:
            self.lifetime = 500

    def update(self) -> None:
        self.position = self.position[0] + self.velocity_x, self.position[1] + self.velocity_y
        self.lifetime -= 1
