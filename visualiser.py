import pygame
from game_map import GameMap
from typing import Tuple


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

    def render_game(self, clicked_mouse_position: Tuple[int, int]) -> None:
        """Render game to the screen
        """
        self.screen.fill((0, 0, 0))
        # Draw grid
        distance = 200
        for i in range(self.game_map.size//distance):
            pygame.draw.line(self.screen, (255, 255, 255), self.game_map.true_to_screen((i * distance, 0)),
                             self.game_map.true_to_screen((i * distance, self.game_map.size)))
            pygame.draw.line(self.screen, (255, 255, 255), self.game_map.true_to_screen((0, i * distance)),
                             self.game_map.true_to_screen((self.game_map.size, i * distance)))

        zoom = self.game_map.zoom
        screen_point = self.game_map.true_to_screen((500, 500))
        pygame.draw.rect(self.screen, (255, 0, 0), (screen_point[0], screen_point[1], 50*zoom, 50*zoom))

        #Draw spaceships
        for spaceship in self.game_map.spaceships:
            body = spaceship.body
            for y in range(len(body)):
                for x in range(len(body[y])):
                    if body[y][x] == 1:
                        top_left_x = self.cell_size*(x-len(body[0])/2)
                        top_left_y = self.cell_size*(y-len(body)/2)
                        true_point_1 = spaceship.ship_to_true((top_left_x, top_left_y))
                        true_point_2 = spaceship.ship_to_true((top_left_x+self.cell_size, top_left_y))
                        true_point_3 = spaceship.ship_to_true((top_left_x+self.cell_size, top_left_y+self.cell_size))
                        true_point_4 = spaceship.ship_to_true((top_left_x, top_left_y+self.cell_size))
                        screen_points = []
                        screen_points.append(self.game_map.true_to_screen(true_point_1))
                        screen_points.append(self.game_map.true_to_screen(true_point_2))
                        screen_points.append(self.game_map.true_to_screen(true_point_3))
                        screen_points.append(self.game_map.true_to_screen(true_point_4))
                        pygame.draw.polygon(self.screen, (0, 0, 255), screen_points)

        # Draw highlight
        if clicked_mouse_position is not None:
            screen_mouse_position = pygame.mouse.get_pos()
            screen_clicked_mouse_position = self.game_map.true_to_screen(clicked_mouse_position)
            pygame.draw.rect(self.screen, (0, 255, 0),
                             (screen_clicked_mouse_position[0], screen_clicked_mouse_position[1],
                              screen_mouse_position[0] - screen_clicked_mouse_position[0],
                              screen_mouse_position[1] - screen_clicked_mouse_position[1]))

        pygame.display.flip()
