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
                             self.game_map.true_to_screen((i * distance, self.game_map.size)))
            pygame.draw.line(self.screen, (255, 255, 255), self.game_map.true_to_screen((0, i * distance)),
                             self.game_map.true_to_screen((self.game_map.size, i * distance)))

        zoom = self.game_map.zoom
        screen_point = self.game_map.true_to_screen((500, 500))
        pygame.draw.rect(self.screen, (255, 0, 0), (screen_point[0], screen_point[1], 50*zoom, 50*zoom))

        # Draw spaceships
        for space_object in self.game_map.space_objects:
            space_object.update()
            body = space_object.body
            for y in range(len(body)):
                for x in range(len(body[y])):
                    if body[y][x] == 1:
                        top_left_x = self.cell_size*(x-len(body[0])/2)
                        top_left_y = self.cell_size*(y-len(body)/2)
                        true_point_1 = space_object.ship_to_true((top_left_x, top_left_y))
                        true_point_2 = space_object.ship_to_true((top_left_x+self.cell_size, top_left_y))
                        true_point_3 = space_object.ship_to_true((top_left_x+self.cell_size, top_left_y+self.cell_size))
                        true_point_4 = space_object.ship_to_true((top_left_x, top_left_y+self.cell_size))
                        screen_points = [self.game_map.true_to_screen(true_point_1),
                                         self.game_map.true_to_screen(true_point_2),
                                         self.game_map.true_to_screen(true_point_3),
                                         self.game_map.true_to_screen(true_point_4)]
                        pygame.draw.polygon(self.screen, (0, 0, 255), screen_points)
            if isinstance(space_object, StarShip) and space_object.selected:
                true_position = self.game_map.true_to_screen(space_object.position)
                pygame.draw.circle(self.screen, (0, 255, 0), true_position, int(space_object.hit_check_range*zoom), 2)
                if space_object.destination is not None:
                    true_destination = self.game_map.true_to_screen(space_object.destination)
                    pygame.draw.line(self.highlight_screen, (0, 255, 0), true_position, true_destination)
                    pygame.draw.circle(self.highlight_screen, (0, 255, 0), true_destination, 6, 1)

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
