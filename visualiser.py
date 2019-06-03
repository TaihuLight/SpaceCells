# Commit message change
import pygame
from game_map import GameMap
from typing import Tuple, Any, List, Dict
from spaceship import StarShip, Asteroid, Miner
import os


class Visualiser:
    """Visualiser for the game
    width:
        width of the screen
    height:
        height of the screen
    screen:
        !!!!!!!
    game_map:
        stores all objects on the game map
    cell_size:
        size of a cell
    effects:
        effects to be drawn to the screen
    alloy_icon:
        sprite of an alloy
    crystal_icon:
        sprite of a crystal
    scrap_icon:
        sprite of a scrap
    number_sprites:
        sprites of all the numbers
    """
    width: int
    height: int
    screen: pygame.Surface
    highlight_screen: pygame.Surface
    game_map: GameMap
    cell_size: int
    effects: List[Tuple[str, Any]]
    alloy_icon: pygame.image
    crystal_icon: pygame.image
    scrap_icon: pygame.image
    #number_sprites: List[pygame.image]

    def __init__(self, window_width: int, window_height: int, game_map: GameMap, cell_size: int) -> None:
        self.width = window_width
        self.height = window_height
        self.screen = pygame.display.set_mode((window_width, window_height))
        self.game_map = game_map
        self.cell_size = cell_size
        self.effects = []
        """
        self.font = pygame.font.SysFont('sans', 18)
        print(pygame.font.get_fonts())
        self.text = self.font.render('0123456789', True, (255, 255, 255))
        self.textRect = self.text.get_rect()
        """

        self.alloy_icon = pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\alloy_icon.png'))
        self.crystal_icon = pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\crystal_icon.png'))
        self.scrap_icon = pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\scrap_icon.png'))
        self.number_sprites = [pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\0.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\1.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\2.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\3.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\4.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\5.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\6.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\7.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\8.png')),
                               pygame.image.load(os.path.join(os.path.dirname(__file__), 'images\\9.png'))]

        self.highlight_screen = pygame.Surface((window_width, window_height))
        self.highlight_screen.set_colorkey((0, 0, 0))
        self.highlight_screen.set_alpha(100)

    def render_game(self, clicked_mouse_position: Tuple[int, int]) -> None:
        """Render game to the screen
        """
        # Wipe screen
        self.screen.fill((0, 0, 0))

        # Wipe highlight screen
        self.highlight_screen.fill((0, 0, 0))
        self.highlight_screen.set_colorkey((0, 0, 0))

        # Draw grid
        distance = 200
        for i in range(self.game_map.size//distance):
            pygame.draw.line(self.screen, (255, 255, 255), self.game_map.true_to_screen((i * distance, 0)),
                             self.game_map.true_to_screen((i * distance, self.game_map.size-distance)))
            pygame.draw.line(self.screen, (255, 255, 255), self.game_map.true_to_screen((0, i * distance)),
                             self.game_map.true_to_screen((self.game_map.size-distance, i * distance)))

        self.draw_objects()
        self.draw_bullets()
        self.draw_effects()
        self.draw_highlight_box(clicked_mouse_position)
        self.screen.blit(self.highlight_screen, (0, 0))
        self.draw_hud()

        pygame.display.flip()

    def draw_objects(self) -> None:
        x_offset = self.game_map.x_offset
        y_offset = self.game_map.y_offset
        zoom = self.game_map.zoom
        for space_object in self.game_map.space_objects:
            if (-x_offset <= space_object.position[0] <= -x_offset + self.width/zoom) and \
                    (-y_offset <= space_object.position[1] <= -y_offset + self.height/zoom):
                body = space_object.body
                if space_object.faction == 'player':
                    hull_colour = (75, 75, 255)
                    armor_colour = (0, 0, 255)
                    turret_colour = (0, 100, 255)
                elif space_object.faction == 'pirate':
                    hull_colour = (255, 200, 0)
                    armor_colour = (255, 0, 0)
                    turret_colour = (255, 70, 0)
                elif space_object.faction == 'neutral':
                    if space_object.name == 'asteroid':
                        hull_colour = (102, 51, 0)
                        armor_colour = (204, 68, 45)
                    else:
                        hull_colour = (65, 65, 65)
                        armor_colour = (45, 45, 45)
                        turret_colour = (30, 30, 30)

                top_left_point = self.cell_size * (-len(body[0]) / 2), self.cell_size * (-len(body) / 2)
                top_second_left_point = self.cell_size * (-len(body[0]) / 2) + self.cell_size, self.cell_size * (-len(body) / 2)
                point1 = self.game_map.true_to_screen_float(space_object.ship_to_true(top_left_point))
                point2 = self.game_map.true_to_screen_float(space_object.ship_to_true(top_second_left_point))
                x_difference = point2[0] - point1[0]
                y_difference = point2[1] - point1[1]
                for y in range(len(body)):
                    for x in range(len(body[y])):
                        if body[y][x] != 0:
                            base_point_x = point1[0] + x_difference * x - y_difference * y
                            base_point_y = point1[1] + y_difference * x + x_difference * y
                            screen_points = [(round(base_point_x), round(base_point_y)),
                                             (round(base_point_x - y_difference), round(base_point_y + x_difference)),
                                             (round(base_point_x - y_difference + x_difference), round(base_point_y + y_difference + x_difference)),
                                             (round(base_point_x + x_difference), round(base_point_y + y_difference))]
                            if body[y][x] == 1:
                                pygame.draw.polygon(self.screen, hull_colour, screen_points)
                            elif body[y][x] == 2:
                                pygame.draw.polygon(self.screen, armor_colour, screen_points)
                            elif body[y][x] == 3 or body[y][x] == 4:
                                pygame.draw.polygon(self.screen, turret_colour, screen_points)

                # Update effects
                if isinstance(space_object, Miner):
                    if space_object.target_cell:
                        target = space_object.selected_target
                        point1 = self.game_map.true_to_screen(
                            space_object.ship_to_true(space_object.body_to_ship(space_object.drill)))
                        point2 = self.game_map.true_to_screen(
                            target.ship_to_true(target.body_to_ship(space_object.target_cell)))
                        self.effects.append(('mining_beam', (point1, point2, space_object.mining_charge)))

                # Draw selection circle if starship selected
                if isinstance(space_object, StarShip) and space_object.selected:
                    true_position = self.game_map.true_to_screen(space_object.position)
                    pygame.draw.circle(self.screen, (0, 255, 0), true_position, int(space_object.hit_check_range*zoom), 2)
                    # Draw target circle and line
                    if space_object.selected_target is not None:
                        target_ship = space_object.selected_target
                        true_target_position = self.game_map.true_to_screen(target_ship.position)
                        if space_object.selected_target.faction == 'neutral':
                            target_colour = (255, 255, 35)
                        else:
                            target_colour = (255, 0, 0)
                        pygame.draw.circle(self.screen, target_colour, true_target_position,
                                           int(target_ship.hit_check_range * zoom), 2)
                        pygame.draw.line(self.highlight_screen, target_colour, true_position, true_target_position)
                    # Draw destination circle and line
                    elif space_object.destination is not None:
                        true_destination = self.game_map.true_to_screen(space_object.destination)
                        pygame.draw.line(self.highlight_screen, (0, 255, 0), true_position, true_destination)
                        pygame.draw.circle(self.highlight_screen, (0, 255, 0), true_destination, 6, 1)

    def draw_bullets(self) -> None:
        zoom = self.game_map.zoom
        for bullet in self.game_map.bullets:
            if bullet.faction == 'player':
                bullet_colour = (0, 70, 112)
            elif bullet.faction == 'pirate':
                bullet_colour = (210, 0, 64)
            screen_position = self.game_map.true_to_screen(bullet.position)
            if bullet.damage == 1:
                pygame.draw.circle(self.screen, bullet_colour, screen_position, int(3 * zoom))
            elif bullet.damage == 2:
                pygame.draw.circle(self.screen, bullet_colour, screen_position, int(5 * zoom))

    def draw_effects(self) -> None:
        while self.effects:
            effect = self.effects.pop()
            if effect[0] == 'mining_beam':
                point1 = effect[1][0]
                point2 = effect[1][1]
                charge = effect[1][2]
                pygame.draw.line(self.screen, (230, 130 - charge*2, 0), point1, point2, int(3 * self.game_map.zoom))

    def draw_highlight_box(self, clicked_mouse_position: Tuple[int, int]) -> None:
        if clicked_mouse_position is not None:
            screen_mouse_position = pygame.mouse.get_pos()
            screen_clicked_mouse_position = self.game_map.true_to_screen(clicked_mouse_position)
            pygame.draw.rect(self.highlight_screen, (0, 255, 0),
                             (screen_clicked_mouse_position[0], screen_clicked_mouse_position[1],
                              screen_mouse_position[0] - screen_clicked_mouse_position[0],
                              screen_mouse_position[1] - screen_clicked_mouse_position[1]))

    def draw_hud(self) -> None:
        center = self.width//2
        pygame.draw.polygon(self.screen, (0, 153, 51), [(center - 300, 0), (center + 300, 0),
                                                        (center + 270, 30), (center - 270, 30)])
        # Draw alloy icon and amount
        self.screen.blit(self.alloy_icon, (center - 270, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['alloy'] % 1000 // 100], (center - 246, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['alloy'] % 100 // 10], (center - 230, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['alloy'] % 10], (center - 214, 5))
        # Draw crystal icon and amount
        self.screen.blit(self.crystal_icon, (center - 190, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['crystal'] % 1000 // 100], (center - 166, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['crystal'] % 100 // 10], (center - 150, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['crystal'] % 10], (center - 134, 5))
        # Draw scrap icon snd amount
        self.screen.blit(self.scrap_icon, (center - 110, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['scrap'] % 1000 // 100], (center - 86, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['scrap'] % 100 // 10], (center - 70, 5))
        self.screen.blit(self.number_sprites[self.game_map.resources['scrap'] % 10], (center - 54, 5))
        """
        self.screen.blit(self.text, self.textRect)
        """