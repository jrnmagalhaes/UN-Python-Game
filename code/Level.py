import sys

import pygame

from code.Const import (WIN_WIDTH, C_BLACK, HUD_HEIGHT, FPS, MAX_DT, LEVEL_COUNT, LEVEL_WIN, LEVEL_QUIT, FONT_NAME,
                        TILE_SIZE,
                        C_WHITE, C_GRAY, C_YELLOW, C_HUD_BG, C_MARK_ENEMY, C_MARK_ROUTE,
                        C_DEBUG_SOLID, C_DEBUG_BODY, C_DEBUG_ATTACK, C_DEBUG_ATTACK_IDLE,
                        KEY_BACK, KEY_DEBUG_WIN, KEY_DEBUG_HITBOX)
from code.LevelData import LEVELS
from code.Player import Player
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
        self.show_hitbox = False
        self.player = Player(self.tilemap.player_start, self.tilemap.solid_rects)

    @property
    def enemies_left(self) -> int:
        return len(self.tilemap.enemies)

    def run(self) -> str:
        self.clock.tick()
        self.dt = 0.0
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
                    if event.key in KEY_DEBUG_HITBOX:
                        self.show_hitbox = not self.show_hitbox
                self.player.handle_event(event)
            self.player.update(self.dt)
            self.draw()
            pygame.display.flip()
            ms = self.clock.tick(FPS)
            self.elapsed_ms += ms
            self.dt = min(ms / 1000, MAX_DT)

    def draw(self):
        self.window.fill(C_BLACK)
        self.window.blit(self.tilemap.surface, self.tilemap.rect)
        self.window.blit(self.route_layer, (0, 0))
        self._draw_markers()
        self.player.draw(self.window)
        if self.show_hitbox:
            self._draw_hitboxes()
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
        for i, enemy in enumerate(self.tilemap.enemies, start=1):
            start = enemy['route'][0]
            pygame.draw.circle(self.window, C_MARK_ENEMY, start, radius)
            self._text(self.font_mark, f'E{i}', C_WHITE, start)

    def _draw_hitboxes(self):
        for wall in self.tilemap.solid_rects:
            pygame.draw.rect(self.window, C_DEBUG_SOLID, wall, 1)
        pygame.draw.rect(self.window, C_DEBUG_BODY, self.player.hitbox, 2)
        tip = self.player.pos + self.player.facing * 40
        pygame.draw.line(self.window, C_DEBUG_BODY, self.player.pos, tip, 1)
        attack = self.player.attack_hitbox()
        if attack:
            pygame.draw.rect(self.window, C_DEBUG_ATTACK, attack, 3)
        elif self.player.attacking:
            pygame.draw.rect(self.window, C_DEBUG_ATTACK_IDLE, self.player.attack_area(), 1)

    def _draw_hud(self):
        pygame.draw.rect(self.window, C_HUD_BG, (0, 0, WIN_WIDTH, HUD_HEIGHT))
        y = HUD_HEIGHT // 2
        level_surf = self.font_hud.render(f'FASE {self.index + 1}/{LEVEL_COUNT} – {self.data["name"]}', True, C_YELLOW)
        self.window.blit(level_surf, level_surf.get_rect(midleft=(16, y)))
        total = format_time(self.previous_time_ms + self.elapsed_ms)
        self._text(self.font_hud, f'TEMPO {total}', C_WHITE, (WIN_WIDTH // 2, y))
        enemy_surf = self.font_hud.render(f'INIMIGOS: {self.enemies_left}', True, C_WHITE)
        self.window.blit(enemy_surf, enemy_surf.get_rect(midright=(WIN_WIDTH - 16, y)))
        hint = self.font_hint.render('ESC – Menu   N – Pular fase   H – Hitbox', True, C_GRAY)
        self.window.blit(hint, hint.get_rect(midright=(enemy_surf.get_rect(midright=(WIN_WIDTH - 16, y)).left - 30, y)))

    def _text(self, font: pygame.font.Font, text: str, color, center: tuple):
        surf = font.render(text, True, color)
        self.window.blit(surf, surf.get_rect(center=center))
