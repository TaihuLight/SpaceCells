# Commit message change
import pygame
from game_map import GameMap
from typing import Tuple
from spaceship import StarShip


class Visualiser:
    """Visualiser for the game
    width:
        width of the screen
    height:
        height of the screen
    screen:
        !!!!!!!
    map:
        stores all objects on the game map
    cell_size:
        size of a cell
    """
    width: int
    height: int
    screen: pygame.Surface
    game_map: GameMap
    cell_size: int

    def __init__(self, window_width: int, window_height: int, game_map: GameMap, cell_size: int) -> None:
        self.width = window_width
        self.height = window_height
        self.screen = pygame.display.set_mode((window_width, window_height))
        self.game_map = game_map
        self.cell_size = cell_size

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

        zoom = self.game_map.zoom

        # Draw all space objects
        for space_object in self.game_map.space_objects:
            body = space_object.body
            if space_object.faction == 'player':
                hull_colour = (75, 75, 255)
                armor_colour = (0, 0, 255)
                turret_colour = (0, 100, 255)
            elif space_object.faction == 'enemy':
                hull_colour = (255, 75, 75)
                armor_colour = (255, 0, 0)
                turret_colour = (255, 70, 0)
            elif space_object.faction == 'neutral':
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
                        elif body[y][x] == 3:
                            pygame.draw.polygon(self.screen, turret_colour, screen_points)

            # Draw selection circle and destination line if starship selected
            if isinstance(space_object, StarShip) and space_object.selected:
                true_position = self.game_map.true_to_screen(space_object.position)
                pygame.draw.circle(self.screen, (0, 255, 0), true_position, int(space_object.hit_check_range*zoom), 2)
                if space_object.destination is not None:
                    true_destination = self.game_map.true_to_screen(space_object.destination)
                    pygame.draw.line(self.highlight_screen, (0, 255, 0), true_position, true_destination)
                    pygame.draw.circle(self.highlight_screen, (0, 255, 0), true_destination, 6, 1)

        # Draw all bullets
            for bullet in self.game_map.bullets:
                if bullet.faction == 'player':
                    bullet_colour = (0, 70, 112)
                elif bullet.faction == 'enemy':
                    bullet_colour = (210, 0, 64)
                true_position = self.game_map.true_to_screen(bullet.position)
                pygame.draw.circle(self.screen, bullet_colour, true_position, int(3 * zoom))

        # Draw highlight box
        if clicked_mouse_position is not None:
            screen_mouse_position = pygame.mouse.get_pos()
            screen_clicked_mouse_position = self.game_map.true_to_screen(clicked_mouse_position)
            pygame.draw.rect(self.highlight_screen, (0, 255, 0),
                             (screen_clicked_mouse_position[0], screen_clicked_mouse_position[1],
                              screen_mouse_position[0] - screen_clicked_mouse_position[0],
                              screen_mouse_position[1] - screen_clicked_mouse_position[1]))

        self.screen.blit(self.highlight_screen, (0, 0))

        pygame.display.flip()
