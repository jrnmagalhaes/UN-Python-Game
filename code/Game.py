import sys

import pygame

from code.Const import WIN_WIDTH, WIN_HEIGHT, WIN_TITLE, MENU_OPTION, LEVEL_COUNT, LEVEL_WIN
from code.Level import Level
from code.Menu import Menu
from code.Score import Score


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WIN_TITLE)
        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    def run(self):
        menu = Menu(self.window)
        while True:
            choice = menu.run()
            if choice == MENU_OPTION[0]:
                self.new_game()
            elif choice == MENU_OPTION[1]:
                Score(self.window).show()
            elif choice == MENU_OPTION[2]:
                self.quit()

    def new_game(self):
        total_ms = 0
        for index in range(LEVEL_COUNT):
            level = Level(self.window, index, total_ms)
            result = level.run()
            total_ms += level.elapsed_ms
            if result != LEVEL_WIN:
                return
        Score(self.window).save_run(total_ms)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()
