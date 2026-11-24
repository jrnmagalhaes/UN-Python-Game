import sys

import pygame

from code.Const import (WIN_WIDTH, WIN_HEIGHT, WIN_TITLE, FPS, MENU_OPTION, LEVEL_COUNT, LEVEL_WIN,
                        C_WHITE, C_GRAY, C_DARK, C_YELLOW, C_BLOOD, FONT_NAME, KEY_BACK, KEY_CONFIRM)
from code.Level import Level, format_time
from code.Menu import Menu


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WIN_TITLE)
        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()

    def run(self):
        menu = Menu(self.window)
        while True:
            choice = menu.run()
            if choice == MENU_OPTION[0]:
                self.new_game()
            elif choice == MENU_OPTION[1]:
                self.stub_screen('PARTIDAS FINALIZADAS', 'Nenhuma partida registrada ainda.')
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
        self.victory_screen(total_ms)

    def victory_screen(self, total_ms: int):
        font_title = pygame.font.SysFont(FONT_NAME, 64, bold=True)
        font_text = pygame.font.SysFont(FONT_NAME, 28)
        font_hint = pygame.font.SysFont(FONT_NAME, 20)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and (event.key in KEY_BACK or event.key in KEY_CONFIRM):
                    return
            self.window.fill(C_DARK)
            for font, text, color, y in ((font_title, 'VOCÊ SOBREVIVEU!', C_BLOOD, WIN_HEIGHT // 2 - 70),
                                         (font_text, f'Tempo total: {format_time(total_ms)}', C_YELLOW, WIN_HEIGHT // 2 + 10),
                                         (font_hint, 'ENTER / ESC – Voltar ao menu', C_GRAY, WIN_HEIGHT // 2 + 80)):
                surf = font.render(text, True, color)
                self.window.blit(surf, surf.get_rect(center=(WIN_WIDTH // 2, y)))
            pygame.display.flip()
            self.clock.tick(FPS)

    def stub_screen(self, title: str, message: str):
        font_title = pygame.font.SysFont(FONT_NAME, 48, bold=True)
        font_text = pygame.font.SysFont(FONT_NAME, 24)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key in KEY_BACK:
                    return
            self.window.fill(C_DARK)
            for font, text, color, y in ((font_title, title, C_YELLOW, WIN_HEIGHT // 2 - 60),
                                         (font_text, message, C_WHITE, WIN_HEIGHT // 2),
                                         (font_text, 'ESC – Voltar ao menu', C_GRAY, WIN_HEIGHT // 2 + 60)):
                surf = font.render(text, True, color)
                self.window.blit(surf, surf.get_rect(center=(WIN_WIDTH // 2, y)))
            pygame.display.flip()
            self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()
