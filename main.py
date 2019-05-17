import pygame
from visualiser import Visualiser
from game_map import GameMap


def game_loop():
    game_running = True
    game_map = GameMap(2000, 1600, 900)
    visualiser = Visualiser(1600, 900, game_map, 20)
    pygame.init()
    right_mouse_pressed = False
    clicked_mouse_position = None
    while game_running:
        event = pygame.event.poll()

        if event.type == pygame.QUIT:
            game_running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_mouse_position = pygame.mouse.get_pos()
                clicked_mouse_position = game_map.screen_to_true(clicked_mouse_position)
            elif event.button == 3:
                right_mouse_pressed = True
            elif event.button == 5:
                game_map.change_zoom(-0.1)
            elif event.button == 4:
                game_map.change_zoom(0.1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                clicked_mouse_position = None
            elif event.button == 3:
                right_mouse_pressed = False

        elif event.type == pygame.MOUSEMOTION:
            if right_mouse_pressed:
                game_map.pan(pygame.mouse.get_rel())
            else:
                #  update the location of the mouse for get_rel
                pygame.mouse.get_rel()

        #current_mouse_position = pygame.mouse.get_pos()
        visualiser.render_game(clicked_mouse_position)


if __name__ == '__main__':
    game_loop()
