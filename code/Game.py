import sys

import pygame

from code.Const import (WIN_WIDTH, WIN_HEIGHT, WIN_TITLE, FPS, MENU_OPTION,
                        C_WHITE, C_GRAY, C_DARK, C_YELLOW, FONT_NAME, KEY_BACK)
from code.Menu import Menu


class Game:
    """Controla a janela e despacha as opções escolhidas no menu."""

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
                # TODO (Etapa 2): fases do jogo
                self.stub_screen('NOVO JOGO', 'As fases serão implementadas em breve.')
            elif choice == MENU_OPTION[1]:
                # TODO (Etapa 5): lista de partidas salvas
                self.stub_screen('PARTIDAS FINALIZADAS', 'Nenhuma partida registrada ainda.')
            elif choice == MENU_OPTION[2]:
                self.quit()

    def stub_screen(self, title: str, message: str):
        """Tela provisória que volta ao menu com ESC."""
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
