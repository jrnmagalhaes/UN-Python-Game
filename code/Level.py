import sys

import pygame

from code.Audio import Audio
from code.Const import (WIN_WIDTH, C_BLACK, HUD_HEIGHT, FPS, MAX_DT, LEVEL_COUNT, LEVEL_WIN, LEVEL_QUIT, FONT_NAME,
                        C_WHITE, C_GRAY, C_YELLOW, C_BLOOD, C_PANEL, C_HUD_BG,
                        C_DEBUG_SOLID, C_DEBUG_BODY, C_DEBUG_ATTACK, C_DEBUG_ATTACK_IDLE, C_DEBUG_ENEMY, C_DEBUG_BACK,
                        BACKSTAB_ANGLE, PLAYER_ATTACK_REACH, SEEN_DELAY, CLEAR_DELAY, HINT_TIME,
                        MSG_SEEN, MSG_CLEAR, MSG_FRONT, KEY_BACK, KEY_DEBUG_WIN, KEY_DEBUG_HITBOX,
                        MUSIC_LEVEL, SFX_ENEMY_DEATH, SFX_ENEMY_NOISE, SFX_SEEN, SFX_RESTART, SFX_LEVEL_CLEAR,
                        VOL_SFX, VOL_ENEMY)
from code.Enemy import Enemy
from code.LevelData import LEVELS
from code.Mediator import Mediator
from code.Player import Player
from code.TileMap import TileMap

STATE_PLAY = 'play'
STATE_SEEN = 'seen'
STATE_CLEAR = 'clear'


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
        self.font_hint = pygame.font.SysFont(FONT_NAME, 14)
        self.font_msg = pygame.font.SysFont(FONT_NAME, 44, bold=True)
        self.font_tip = pygame.font.SysFont(FONT_NAME, 18, bold=True)
        self.view_layer = pygame.Surface(window.get_size(), pygame.SRCALPHA)
        self.show_hitbox = False
        self.reset()

    def reset(self):
        self.player = Player(self.tilemap.player_start, self.tilemap.solid_rects)
        self.enemies = [Enemy(e['route'], e['loop'], e['pause'], seed=i) for i, e in enumerate(self.tilemap.enemies)]
        self.state = STATE_PLAY
        self.state_timer = 0.0
        self.watcher = None
        self.tip_timer = 0.0

    @property
    def enemies_left(self) -> int:
        return sum(1 for e in self.enemies if e.alive)

    def run(self) -> str:
        Audio.play_music(MUSIC_LEVEL)  # não reinicia se já tocava (fase anterior / reinício)
        self.clock.tick()
        self.dt = 0.0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if Audio.handle_event(event):
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key in KEY_BACK:
                        return LEVEL_QUIT
                    if event.key in KEY_DEBUG_WIN:
                        return LEVEL_WIN
                    if event.key in KEY_DEBUG_HITBOX:
                        self.show_hitbox = not self.show_hitbox
                if self.state == STATE_PLAY:
                    self.player.handle_event(event)
            if self.update(self.dt):
                return LEVEL_WIN
            self.draw()
            pygame.display.flip()
            ms = self.clock.tick(FPS)
            if self.state != STATE_CLEAR:
                self.elapsed_ms += ms
            self.dt = min(ms / 1000, MAX_DT)

    def update(self, dt: float) -> bool:
        self.tip_timer = max(0.0, self.tip_timer - dt)
        if self.state == STATE_PLAY:
            self.player.update(dt)
            for enemy in self.enemies:
                enemy.update(dt)
            killed, blocked = Mediator.resolve_attack(self.player, self.enemies)
            for _ in killed:
                Audio.play(SFX_ENEMY_DEATH, VOL_SFX)
            for enemy in self.enemies:
                if enemy.noise_due(dt):
                    Audio.play_at(SFX_ENEMY_NOISE, VOL_ENEMY, enemy.pos, self.player.pos)
            if blocked and not killed:
                self.tip_timer = HINT_TIME
            if self.enemies_left == 0:
                self.state = STATE_CLEAR
                self.state_timer = CLEAR_DELAY
                Audio.play(SFX_LEVEL_CLEAR, VOL_SFX)
                return False
            watcher = Mediator.find_watcher(self.player, self.enemies)
            if watcher:
                watcher.alert(self.player.pos)
                self.watcher = watcher
                self.state = STATE_SEEN
                self.state_timer = SEEN_DELAY
                Audio.play(SFX_SEEN, VOL_SFX)
        elif self.state == STATE_SEEN:
            self.watcher.update(dt)
            self.state_timer -= dt
            if self.state_timer <= 0:
                Audio.play(SFX_RESTART, VOL_SFX)
                self.reset()
        elif self.state == STATE_CLEAR:
            for enemy in self.enemies:
                enemy.update(dt)
            self.state_timer -= dt
            return self.state_timer <= 0
        return False

    def draw(self):
        self.window.fill(C_BLACK)
        self.window.blit(self.tilemap.surface, self.tilemap.rect)
        for enemy in self.enemies:
            enemy.draw_floor(self.window)
        self.view_layer.fill((0, 0, 0, 0))
        for enemy in self.enemies:
            enemy.draw_view(self.view_layer)
        self.window.blit(self.view_layer, (0, 0))
        for enemy in self.enemies:
            enemy.draw(self.window)
        self.player.draw(self.window)
        if self.show_hitbox:
            self._draw_hitboxes()
        self._draw_hud()
        if self.state == STATE_SEEN:
            self._draw_banner(MSG_SEEN, C_BLOOD)
        elif self.state == STATE_CLEAR:
            self._draw_banner(MSG_CLEAR, C_YELLOW)
        elif self.tip_timer > 0:
            tip = self.font_tip.render(MSG_FRONT, True, C_YELLOW)
            pos = self.player.pos
            self.window.blit(tip, tip.get_rect(midbottom=(round(pos.x), round(pos.y) - 30)))

    def _draw_banner(self, text: str, color):
        surf = self.font_msg.render(text, True, color)
        rect = surf.get_rect(center=self.tilemap.rect.center)
        panel = pygame.Surface((self.tilemap.rect.width, rect.height + 30), pygame.SRCALPHA)
        panel.fill(C_PANEL)
        self.window.blit(panel, panel.get_rect(center=rect.center))
        self.window.blit(surf, rect)

    def _draw_hitboxes(self):
        for wall in self.tilemap.solid_rects:
            pygame.draw.rect(self.window, C_DEBUG_SOLID, wall, 1)
        layer = pygame.Surface(self.window.get_size(), pygame.SRCALPHA)
        reach = PLAYER_ATTACK_REACH * 2
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            back = -enemy.facing
            half = 180 - BACKSTAB_ANGLE
            arc = [enemy.pos] + [enemy.pos + back.rotate(-half + 2 * half * i / 8) * reach for i in range(9)]
            pygame.draw.polygon(layer, C_DEBUG_BACK, arc)
        self.window.blit(layer, (0, 0))
        for enemy in self.enemies:
            if enemy.alive:
                pygame.draw.rect(self.window, C_DEBUG_ENEMY, enemy.hitbox, 2)
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
        hint = self.font_hint.render('ESC Menu   M Som   N Pular   H Hitbox', True, C_GRAY)
        self.window.blit(hint, hint.get_rect(midright=(enemy_surf.get_rect(midright=(WIN_WIDTH - 16, y)).left - 30, y)))
        Audio.draw_muted(self.window, (self.tilemap.rect.right - 4, HUD_HEIGHT + 4))

    def _text(self, font: pygame.font.Font, text: str, color, center: tuple):
        surf = font.render(text, True, color)
        self.window.blit(surf, surf.get_rect(center=center))
