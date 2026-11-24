import sys

import pygame

from code.Const import (WIN_WIDTH, C_BLACK, HUD_HEIGHT, FPS, LEVEL_COUNT, LEVEL_WIN, LEVEL_QUIT, FONT_NAME, TILE_SIZE,
                        C_WHITE, C_GRAY, C_YELLOW, C_HUD_BG, C_MARK_PLAYER, C_MARK_ENEMY, C_MARK_ROUTE,
                        KEY_BACK, KEY_DEBUG_WIN)
from code.LevelData import LEVELS
from code.TileMap import TileMap


def format_time(ms: int) -> str:
    minutes, rest = divmod(int(ms), 60_000)
    return f'{minutes:02d}:{rest // 1000:02d}.{(rest % 1000) // 10:02d}'


class Level:
    def __init__(self, window: pygame.Surface, index: int, previous_time_ms: int = 0):
        self.window = window
        self.index = index
        self.data = LEVELS[index]
        self.tilemap = TileMap(self.data)
        self.previous_time_ms = previous_time_ms
        self.elapsed_ms = 0
        self.clock = pygame.time.Clock()
        self.font_hud = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.font_mark = pygame.font.SysFont(FONT_NAME, 14, bold=True)
        self.font_hint = pygame.font.SysFont(FONT_NAME, 14)
        self.route_layer = self._build_route_layer()

    @property
    def enemies_left(self) -> int:
        return len(self.tilemap.enemies)

    def run(self) -> str:
        self.clock.tick()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in KEY_BACK:
                        return LEVEL_QUIT
                    if event.key in KEY_DEBUG_WIN:
                        return LEVEL_WIN
            self.draw()
            pygame.display.flip()
            self.elapsed_ms += self.clock.tick(FPS)

    def draw(self):
        self.window.fill(C_BLACK)
        self.window.blit(self.tilemap.surface, self.tilemap.rect)
        self.window.blit(self.route_layer, (0, 0))
        self._draw_markers()
        self._draw_hud()

    def _build_route_layer(self) -> pygame.Surface:
        layer = pygame.Surface(self.window.get_size(), pygame.SRCALPHA)
        color = (*C_MARK_ROUTE, 150)
        for enemy in self.tilemap.enemies:
            route = enemy['route']
            points = route + [route[0]] if enemy['loop'] else route
            if len(points) > 1:
                pygame.draw.lines(layer, color, False, points, 3)
            for p in route:
                pygame.draw.circle(layer, color, p, 5)
        return layer

    def _draw_markers(self):
        radius = TILE_SIZE // 2 - 6
        pygame.draw.circle(self.window, C_MARK_PLAYER, self.tilemap.player_start, radius)
        self._text(self.font_mark, 'P', C_WHITE, self.tilemap.player_start)
        for i, enemy in enumerate(self.tilemap.enemies, start=1):
            start = enemy['route'][0]
            pygame.draw.circle(self.window, C_MARK_ENEMY, start, radius)
            self._text(self.font_mark, f'E{i}', C_WHITE, start)

    def _draw_hud(self):
        pygame.draw.rect(self.window, C_HUD_BG, (0, 0, WIN_WIDTH, HUD_HEIGHT))
        y = HUD_HEIGHT // 2
        level_surf = self.font_hud.render(f'FASE {self.index + 1}/{LEVEL_COUNT} – {self.data["name"]}', True, C_YELLOW)
        self.window.blit(level_surf, level_surf.get_rect(midleft=(16, y)))
        total = format_time(self.previous_time_ms + self.elapsed_ms)
        self._text(self.font_hud, f'TEMPO {total}', C_WHITE, (WIN_WIDTH // 2, y))
        enemy_surf = self.font_hud.render(f'INIMIGOS: {self.enemies_left}', True, C_WHITE)
        self.window.blit(enemy_surf, enemy_surf.get_rect(midright=(WIN_WIDTH - 16, y)))
        hint = self.font_hint.render('ESC – Menu   N – Concluir fase (debug)', True, C_GRAY)
        self.window.blit(hint, hint.get_rect(midright=(enemy_surf.get_rect(midright=(WIN_WIDTH - 16, y)).left - 30, y)))

    def _text(self, font: pygame.font.Font, text: str, color, center: tuple):
        surf = font.render(text, True, color)
        self.window.blit(surf, surf.get_rect(center=center))
