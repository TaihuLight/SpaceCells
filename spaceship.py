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

    def update_position(self):
        self.rotation = self.rotation % (2 * pi)
        self.position = self.position[0] + self.velocity_x, self.position[1] + self.velocity_y

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
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
                    object2_x = int((base_point_x + len(self.body[0]) / 2 * cell_size) // cell_size)
                    object2_y = int((base_point_y + len(self.body) / 2 * cell_size) // cell_size)
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
    turrets:
        Location of all turrets in the body array
    cannons:
        Location of all cannons in the body array
    cannon_cooldown:
        How many ticks until the cannons can fire again
    close_targets:
        A list of angles between this ship and enemy ships in close range
    medium_targets:
        A list of angles between this ship and enemy ships in medium range
    selected_target:
        Enemy ship that is being targeted by this ship
    close_ships:
        A dictionary where keys are distances and values are enemy ships
    """
    acceleration: float
    turn_speed: float
    destination: Optional[Tuple[int, int]]
    selected: bool
    max_speed: float
    turrets: Dict[Tuple[int, int], int]
    cannons: List[Tuple[int, int]]
    cannon_cooldown: int
    close_targets: List[float]
    medium_targets: List[float]
    selected_target: StarShip
    close_ships: Dict[float, StarShip]

    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int],
                 acceleration: float, turn_speed: float, max_speed: float) -> None:
        SpaceObject.__init__(self, name, body, faction, position)
        self.hull = 0
        self.acceleration = acceleration
        self.turn_speed = turn_speed
        self.destination = None
        self.selected = False
        self.max_speed = max_speed
        self.turrets = {}
        self.cannons = []
        self.cannon_cooldown = total_cannon_cooldown
        self.close_targets = []
        self.medium_targets = []
        self.selected_target = None
        self.close_ships = {}
        for i, sublist in enumerate(self.body):
            for j, number in enumerate(sublist):
                if number == 1 or number == 2:
                    self.hull += 1
                elif number == 3:
                    self.turrets[i, j] = randint(0, turret_cooldown)
                    self.hull += 1
                elif number == 4:
                    self.cannons.append((i, j))
                    self.hull += 1

        self.hull = self.hull // 3

    def update(self, bullets: List[Bullet]) -> None:
        if self.destination is not None:
            self.move_to(self.destination)
            if hypot(self.destination[0] - self.position[0], self.destination[1] - self.position[1]) \
                    < self.hit_check_range:
                self.destination = None
        elif self.selected_target is not None:
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
        else:
            self.decelerate()

    def move_to(self, destination: Tuple[float, float]) -> None:
        self.rotate_towards(destination)

        self.velocity_x += self.acceleration * cos(self.rotation)
        self.velocity_y += self.acceleration * sin(self.rotation)

        if hypot(self.velocity_x, self.velocity_y) > self.max_speed:
            velocity_angle = atan2(self.velocity_y, self.velocity_x)
            self.velocity_x = self.max_speed * cos(velocity_angle)
            self.velocity_y = self.max_speed * sin(velocity_angle)

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


class Corvette(StarShip):
    """A corvette class ship with turrets and cannons
    """
    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int],
                 acceleration: float, turn_speed: float, max_speed: float):
        StarShip.__init__(self, name, body, faction, position, acceleration, turn_speed, max_speed)

    def update(self, bullets: List[Bullet]) -> None:
        StarShip.update(self, bullets)

        # Update this ship's turrets
        if self.close_targets:
            for turret_pos in self.turrets:
                self.turrets[turret_pos] -= 1
                if self.turrets[turret_pos] == 0:
                    position = self.ship_to_true(
                        (int(cell_size * (turret_pos[1] - len(self.body[0]) / 2) + cell_size // 2),
                         int(cell_size * (turret_pos[0] - len(self.body) / 2) + cell_size // 2)))
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
                    (int(cell_size * (cannon_pos[1] - len(self.body[0]) / 2) + cell_size // 2),
                     int(cell_size * (cannon_pos[0] - len(self.body) / 2) + cell_size // 2)))
                rotation = self.rotation
                new_bullet = Bullet(position, rotation, self.faction, 2)
                bullets.append(new_bullet)
            self.cannon_cooldown = total_cannon_cooldown

        SpaceObject.update_position(self)
        self.check_damage_from_bullets(bullets)

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
        if 0 <= y < len(self.body) and 0 <= x < len(self.body[0]):
            if self.body[y][x] == 0:
                return False
            elif self.body[y][x] == 1:
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                return True
            elif self.body[y][x] == 2:
                if damage == 1:
                    self.body[y][x] = 1
                    return True
                elif damage == 2:
                    self.body[y][x] = 0
                    if self.hull is not None:
                        self.hull -= 1
                    self.cells -= 1
                    return True
            elif self.body[y][x] == 3:
                del self.turrets[(y, x)]
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                return True
            elif self.body[y][x] == 4:
                self.cannons.remove((y, x))
                self.body[y][x] = 0
                if self.hull is not None:
                    self.hull -= 1
                self.cells -= 1
                return True
        return False


class Asteroid (SpaceObject):
    """A mineable asteroid
    """
    def __init__(self, name: str, body: List[List[int]], faction: str, position: Tuple[int, int]) -> None:
        SpaceObject.__init__(self, name, body, faction, position)
        self.rotation = randint(0, 628) / 100

    def update(self, bullets: List[Bullet]) -> None:
        self.check_damage_from_bullets(bullets)
        self.rotation += 0.001
        SpaceObject.update_position(self)

    def check_damage_from_bullets(self, bullets: List[Bullet]) -> None:
        for bullet in bullets:
            if hypot(bullet.position[0] - self.position[0],
                     bullet.position[1] - self.position[1]) < self.hit_check_range:
                ship_bullet_position = self.true_to_ship(bullet.position)
                x = (ship_bullet_position[0] + int(len(self.body[0]) / 2 * cell_size)) // cell_size
                y = (ship_bullet_position[1] + int(len(self.body) / 2 * cell_size)) // cell_size
                if self.handel_damage(x, y, bullet.damage):
                    bullets.remove(bullet)

    def handel_damage(self, x: int, y: int, damage: int) -> bool:
        if 0 <= y < len(self.body) and 0 <= x < len(self.body[0]):
            if self.body[y][x] == 1 or self.body[y][x] == 2:
                self.body[y][x] = 0
                self.cells -= 1
                return True
        return False


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
