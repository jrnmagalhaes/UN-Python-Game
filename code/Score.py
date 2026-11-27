import sys
from datetime import datetime

import pygame

from code.Const import (WIN_WIDTH, WIN_HEIGHT, FPS, MENU_BG, DB_PATH, DB_DATE_FORMAT, SCORE_DATE_FORMAT,
                        NAME_MAX_LEN, NAME_EXTRA_CHARS, C_WHITE, C_GRAY, C_BLOOD, C_YELLOW, C_PANEL, C_BG_DIM,
                        FONT_NAME, KEY_BACK, KEY_CONFIRM, MUSIC_MENU, SFX_WIN, VOL_SFX)
from code.Audio import Audio
from code.DBProxy import DBProxy
from code.Level import format_time


def format_date(text: str) -> str:
    try:
        return datetime.strptime(text, DB_DATE_FORMAT).strftime(SCORE_DATE_FORMAT)
    except ValueError:
        return text


class Score:

    def __init__(self, window: pygame.Surface, db_path: str = DB_PATH):
        self.window = window
        self.db_path = db_path
        self.clock = pygame.time.Clock()
        self.background = self._make_background()
        self.font_title = pygame.font.SysFont(FONT_NAME, 56, bold=True)
        self.font_text = pygame.font.SysFont(FONT_NAME, 28, bold=True)
        self.font_row = pygame.font.SysFont(FONT_NAME, 24)
        self.font_row_bold = pygame.font.SysFont(FONT_NAME, 24, bold=True)
        self.font_hint = pygame.font.SysFont(FONT_NAME, 20)

    # ---------- telas ----------

    def save_run(self, total_ms: int):
        name = ''
        warning = ''
        Audio.stop_music()
        Audio.play(SFX_WIN, VOL_SFX)
        pygame.key.start_text_input()  # letras chegam como TEXTINPUT (inclui acentos de teclas mortas)
        pygame.event.clear(pygame.TEXTINPUT)  # descarta letras digitadas ainda durante a fase
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.TEXTINPUT:
                    for char in event.text:
                        if self._valid_char(char, name):
                            name += char
                            warning = ''
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key in KEY_BACK:
                    return
                if event.key in KEY_CONFIRM:
                    if name.strip():
                        self.show(self._save(name.strip(), total_ms))
                        return
                    warning = 'Digite ao menos 1 caractere.'
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

            self._draw_victory(total_ms, name, warning)
            pygame.display.flip()
            self.clock.tick(FPS)

    def show(self, highlight_id: int = None):
        db = DBProxy(self.db_path)
        runs = db.top10()
        db.close()
        Audio.play_music(MUSIC_MENU)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if Audio.handle_event(event):
                    continue
                if event.type == pygame.KEYDOWN and (event.key in KEY_BACK or event.key in KEY_CONFIRM):
                    return
            self._draw_list(runs, highlight_id)
            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------- lógica ----------

    def _save(self, name: str, total_ms: int) -> int:
        db = DBProxy(self.db_path)
        run_id = db.save(name, total_ms)
        db.close()
        return run_id

    @staticmethod
    def _valid_char(char: str, name: str) -> bool:
        if len(char) != 1 or len(name) >= NAME_MAX_LEN:
            return False
        if char == ' ' and not name:
            return False
        return char.isalnum() or char in NAME_EXTRA_CHARS

    # ---------- desenho ----------

    def _make_background(self) -> pygame.Surface:
        bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), depth=24)
        image = pygame.image.load(MENU_BG).convert()
        bg.blit(pygame.transform.smoothscale(image, (WIN_WIDTH, WIN_HEIGHT)), (0, 0))
        dim = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        dim.fill(C_BG_DIM)
        bg.blit(dim, (0, 0))
        return bg.convert()

    def _draw_title(self, text: str, color, y: int):
        self._text(self.font_title, text, (0, 0, 0), (WIN_WIDTH // 2 + 3, y + 3))
        self._text(self.font_title, text, color, (WIN_WIDTH // 2, y))

    def _draw_victory(self, total_ms: int, name: str, warning: str):
        self.window.blit(self.background, (0, 0))
        self._draw_title('VOCÊ SOBREVIVEU!', C_BLOOD, 120)
        self._text(self.font_text, f'Tempo total: {format_time(total_ms)}', C_YELLOW, (WIN_WIDTH // 2, 210))
        self._text(self.font_row, 'Digite seu nome:', C_WHITE, (WIN_WIDTH // 2, 300))

        box = pygame.Rect(0, 0, 320, 56)
        box.center = (WIN_WIDTH // 2, 360)
        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        panel.fill(C_PANEL)
        self.window.blit(panel, box)
        pygame.draw.rect(self.window, C_YELLOW, box, 2)
        cursor = '_' if (pygame.time.get_ticks() // 500) % 2 == 0 and len(name) < NAME_MAX_LEN else ' '
        self._text(self.font_text, name + cursor, C_WHITE, box.center)
        self._text(self.font_hint, f'{len(name)}/{NAME_MAX_LEN}', C_GRAY, (box.right + 36, box.centery))

        if warning:
            self._text(self.font_hint, warning, C_BLOOD, (WIN_WIDTH // 2, 420))
        self._text(self.font_hint, 'ENTER – Salvar      BACKSPACE – Apagar      ESC – Sair sem salvar',
                   C_GRAY, (WIN_WIDTH // 2, WIN_HEIGHT - 50))
        Audio.draw_muted(self.window, (WIN_WIDTH - 12, 12))

    def _draw_list(self, runs: list, highlight_id: int):
        self.window.blit(self.background, (0, 0))
        self._draw_title('PARTIDAS FINALIZADAS', C_YELLOW, 70)

        columns = ((210, 'POS'), (290, 'NOME'), (510, 'TEMPO'), (650, 'DATA'))
        panel = pygame.Rect(0, 0, 680, 420)
        panel.midtop = (WIN_WIDTH // 2, 130)
        surf = pygame.Surface(panel.size, pygame.SRCALPHA)
        surf.fill(C_PANEL)
        self.window.blit(surf, panel)

        header_y = panel.top + 28
        for x, title in columns:
            self._text_left(self.font_row_bold, title, C_YELLOW, (x, header_y))
        pygame.draw.line(self.window, C_GRAY, (panel.left + 20, header_y + 20), (panel.right - 20, header_y + 20), 1)

        if not runs:
            self._text(self.font_row, 'Nenhuma partida registrada ainda.', C_WHITE, (WIN_WIDTH // 2, panel.centery))
        for i, (run_id, name, time_ms, date) in enumerate(runs):
            y = header_y + 44 + i * 36
            color = C_YELLOW if run_id == highlight_id else C_WHITE
            font = self.font_row_bold if run_id == highlight_id else self.font_row
            for (x, _), value in zip(columns, (f'{i + 1}º', name, format_time(time_ms), format_date(date))):
                self._text_left(font, value, color, (x, y))

        if highlight_id is not None and all(run[0] != highlight_id for run in runs):
            self._text(self.font_hint, 'Sua partida foi salva, mas ficou fora do top 10.', C_GRAY,
                       (WIN_WIDTH // 2, panel.bottom + 22))
        self._text(self.font_hint, 'ESC – Voltar ao menu      M – Som', C_GRAY, (WIN_WIDTH // 2, WIN_HEIGHT - 28))
        Audio.draw_muted(self.window, (WIN_WIDTH - 12, 12))

    def _text(self, font: pygame.font.Font, text: str, color, center: tuple):
        surf = font.render(text, True, color)
        self.window.blit(surf, surf.get_rect(center=center))

    def _text_left(self, font: pygame.font.Font, text: str, color, midleft: tuple):
        surf = font.render(text, True, color)
        self.window.blit(surf, surf.get_rect(midleft=midleft))

    @staticmethod
    def _quit():
        pygame.quit()
        sys.exit()
