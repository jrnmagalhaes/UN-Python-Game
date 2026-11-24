import sys

import pygame

from code.Const import (WIN_WIDTH, WIN_HEIGHT, FPS, MENU_BG, MENU_OPTION, MENU_COMMANDS,
                        C_WHITE, C_GRAY, C_BLOOD, C_YELLOW, C_PANEL, FONT_NAME,
                        KEY_UP, KEY_DOWN, KEY_CONFIRM)


class Menu:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.clock = pygame.time.Clock()
        bg = pygame.image.load(MENU_BG).convert()
        self.background = pygame.transform.smoothscale(bg, (WIN_WIDTH, WIN_HEIGHT))
        self.font_title = pygame.font.SysFont(FONT_NAME, 96, bold=True)
        self.font_option = pygame.font.SysFont(FONT_NAME, 34, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 20)
        self.font_small_bold = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.selected = 0

    def run(self) -> str:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in KEY_DOWN:
                        self.selected = (self.selected + 1) % len(MENU_OPTION)
                    elif event.key in KEY_UP:
                        self.selected = (self.selected - 1) % len(MENU_OPTION)
                    elif event.key in KEY_CONFIRM:
                        return MENU_OPTION[self.selected]
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def draw(self):
        self.window.blit(self.background, (0, 0))

        self._text(self.font_title, 'SURVIVE', (0, 0, 0), (WIN_WIDTH // 2 + 4, 104))
        self._text(self.font_title, 'SURVIVE', C_BLOOD, (WIN_WIDTH // 2, 100))

        for i, option in enumerate(MENU_OPTION):
            y = 250 + i * 60
            if i == self.selected:
                self._text(self.font_option, f'>  {option}  <', C_YELLOW, (WIN_WIDTH // 2, y))
            else:
                self._text(self.font_option, option, C_WHITE, (WIN_WIDTH // 2, y))

        panel = pygame.Surface((420, 40 + len(MENU_COMMANDS) * 28), pygame.SRCALPHA)
        panel.fill(C_PANEL)
        panel_rect = panel.get_rect(midbottom=(WIN_WIDTH // 2, WIN_HEIGHT - 20))
        self.window.blit(panel, panel_rect)
        self._text(self.font_small_bold, 'COMANDOS', C_YELLOW, (panel_rect.centerx, panel_rect.top + 18))
        for i, (key, action) in enumerate(MENU_COMMANDS):
            y = panel_rect.top + 48 + i * 28
            key_surf = self.font_small_bold.render(key, True, C_WHITE)
            self.window.blit(key_surf, key_surf.get_rect(midright=(panel_rect.centerx - 15, y)))
            act_surf = self.font_small.render(f'–  {action}', True, C_GRAY)
            self.window.blit(act_surf, act_surf.get_rect(midleft=(panel_rect.centerx - 5, y)))

    def _text(self, font: pygame.font.Font, text: str, color, center: tuple):
        surf = font.render(text, True, color)
        self.window.blit(surf, surf.get_rect(center=center))
