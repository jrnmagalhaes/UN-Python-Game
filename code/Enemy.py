import random

import pygame
from pygame.math import Vector2

from code.Animation import Animation
from code.Assets import load_frames
from code.Const import (ENEMY_DIR, ENEMY_SCALE, ENEMY_PIVOTS, ENEMY_HITBOX, ENEMY_SPEED, ENEMY_TURN_SPEED,
                        ENEMY_ALERT_TURN_SPEED, ENEMY_ANIM_FPS, ENEMY_ATTACK_FPS, ENEMY_FADE_TIME,
                        VIEW_RANGE, VIEW_FOV, C_VIEW_CONE, C_VIEW_EDGE, C_VIEW_ALERT, C_BLOOD_STAIN,
                        ENEMY_NOISE_INTERVAL)
from code.Entity import Entity

STATE_WALK = 'walk'
STATE_PAUSE = 'pause'
STATE_TURN = 'turn'
STATE_ALERT = 'alert'
STATE_DEAD = 'dead'


def _angle_of(direction: Vector2) -> float:
    return -direction.as_polar()[1]


def _angle_diff(target: float, current: float) -> float:
    return (target - current + 180) % 360 - 180


class Enemy(Entity):
    def __init__(self, route: list, loop: bool, pause: float, seed: int = 0):
        super().__init__(route[0], ENEMY_HITBOX)
        self.points = [Vector2(p) for p in route]
        if not loop and len(self.points) > 2:
            self.points += self.points[-2:0:-1]
        self.pause_time = pause
        self.anims = {
            'idle': Animation(load_frames(ENEMY_DIR, ENEMY_SCALE, 'skeleton-idle_'), ENEMY_ANIM_FPS),
            'move': Animation(load_frames(ENEMY_DIR, ENEMY_SCALE, 'skeleton-move_'), ENEMY_ANIM_FPS),
            'attack': Animation(load_frames(ENEMY_DIR, ENEMY_SCALE, 'skeleton-attack_'), ENEMY_ATTACK_FPS, loop=False),
        }
        self.pivots = {k: (x * ENEMY_SCALE, y * ENEMY_SCALE) for k, (x, y) in ENEMY_PIVOTS.items()}
        self.target = 1 % len(self.points)
        self.timer = 0.0
        self.alert_target = None
        self.last_hit_attack = 0
        self.stain = self._build_stain(seed)
        self.noise_timer = random.uniform(*ENEMY_NOISE_INTERVAL)
        if len(self.points) > 1:
            self.angle = _angle_of(self.points[1] - self.pos)
            self.state = STATE_WALK
        else:
            self.state = STATE_PAUSE

    @property
    def alive(self) -> bool:
        return self.state != STATE_DEAD

    @property
    def anim_name(self) -> str:
        if self.state in (STATE_ALERT, STATE_DEAD):
            return 'attack' if self.state == STATE_ALERT else 'idle'
        return 'move' if self.state == STATE_WALK else 'idle'

    def kill(self):
        self.state = STATE_DEAD
        self.timer = ENEMY_FADE_TIME

    def alert(self, target):
        self.state = STATE_ALERT
        self.alert_target = Vector2(target)
        self.anims['attack'].reset()

    def noise_due(self, dt: float) -> bool:
        """True quando chega a hora de resmungar (intervalo aleatório em ENEMY_NOISE_INTERVAL)."""
        if not self.alive:
            return False
        self.noise_timer -= dt
        if self.noise_timer > 0:
            return False
        self.noise_timer = random.uniform(*ENEMY_NOISE_INTERVAL)
        return True

    def turn_towards(self, angle: float, speed: float, dt: float) -> bool:
        diff = _angle_diff(angle, self.angle)
        step = speed * dt
        if abs(diff) <= step:
            self.angle = angle % 360
            return True
        self.angle = (self.angle + (step if diff > 0 else -step)) % 360
        return False

    def update(self, dt: float):
        if self.state == STATE_DEAD:
            self.timer = max(0.0, self.timer - dt)
            return
        if self.state == STATE_ALERT:
            delta = self.alert_target - self.pos
            if delta.length_squared() > 1:
                self.turn_towards(_angle_of(delta), ENEMY_ALERT_TURN_SPEED, dt)
            self.anims['attack'].update(dt)
            return
        if len(self.points) < 2:
            self.anims['idle'].update(dt)
            return

        if self.state == STATE_PAUSE:
            self.timer -= dt
            if self.timer <= 0:
                self.state = STATE_TURN
        if self.state == STATE_TURN:
            if self.turn_towards(_angle_of(self.points[self.target] - self.pos), ENEMY_TURN_SPEED, dt):
                self.state = STATE_WALK
        elif self.state == STATE_WALK:
            goal = self.points[self.target]
            delta = goal - self.pos
            step = ENEMY_SPEED * dt
            if delta.length() <= step:
                self.pos = Vector2(goal)
                self.target = (self.target + 1) % len(self.points)
                self.state = STATE_PAUSE
                self.timer = self.pause_time
            else:
                self.pos += delta.normalize() * step
                self.angle = _angle_of(delta)
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        self.anims[self.anim_name].update(dt)

    def view_polygon(self) -> list:
        steps = 16
        half = VIEW_FOV / 2
        points = [self.pos]
        for i in range(steps + 1):
            points.append(self.pos + self.facing.rotate(-half + VIEW_FOV * i / steps) * VIEW_RANGE)
        return points

    def draw_view(self, layer: pygame.Surface):
        if not self.alive:
            return
        points = self.view_polygon()
        if self.state == STATE_ALERT:
            pygame.draw.polygon(layer, C_VIEW_ALERT, points)
        else:
            pygame.draw.polygon(layer, C_VIEW_CONE, points)
            pygame.draw.lines(layer, C_VIEW_EDGE, True, points, 1)

    def draw_floor(self, surf: pygame.Surface):
        if not self.alive:
            surf.blit(self.stain, self.stain.get_rect(center=(round(self.pos.x), round(self.pos.y))))

    def draw(self, surf: pygame.Surface):
        name = self.anim_name
        image = self.anims[name].frame
        if self.state == STATE_DEAD:
            if self.timer <= 0:
                return
            image = image.copy()
            image.set_alpha(round(255 * self.timer / ENEMY_FADE_TIME))
        self.blit_rotated(surf, image, self.pivots[name])

    @staticmethod
    def _build_stain(seed: int) -> pygame.Surface:
        rng = random.Random(seed)
        size = 44
        stain = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(stain, C_BLOOD_STAIN, (size // 2, size // 2), 11)
        for _ in range(7):
            offset = Vector2(rng.uniform(6, 14), 0).rotate(rng.uniform(0, 360))
            pygame.draw.circle(stain, C_BLOOD_STAIN, (size / 2 + offset.x, size / 2 + offset.y), rng.randint(3, 6))
        return stain
