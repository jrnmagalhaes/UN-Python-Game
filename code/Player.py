import pygame
from pygame.math import Vector2

from code.Animation import Animation
from code.Assets import load_frames
from code.Const import (PLAYER_DIR, PLAYER_SCALE, PLAYER_BODY_PIVOT, PLAYER_HITBOX, PLAYER_SPEED, PLAYER_SLOW_SPEED,
                        PLAYER_ANIM_FPS, PLAYER_FEET_FPS, PLAYER_FEET_SLOW_FPS, PLAYER_ATTACK_FPS,
                        PLAYER_ATTACK_ACTIVE, PLAYER_ATTACK_COOLDOWN, PLAYER_ATTACK_REACH, PLAYER_ATTACK_SIZE,
                        KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SLOW, KEY_ATTACK, MOUSE_ATTACK)
from code.Entity import Entity


def _pressed(keys, group: tuple) -> bool:
    return any(keys[k] for k in group)


class Player(Entity):
    def __init__(self, pos, solids: list):
        super().__init__(pos, PLAYER_HITBOX)
        self.solids = solids
        self.body = {
            'idle': Animation(load_frames(f'{PLAYER_DIR}/knife/idle', PLAYER_SCALE), PLAYER_ANIM_FPS),
            'move': Animation(load_frames(f'{PLAYER_DIR}/knife/move', PLAYER_SCALE), PLAYER_ANIM_FPS),
            'attack': Animation(load_frames(f'{PLAYER_DIR}/knife/meleeattack', PLAYER_SCALE), PLAYER_ATTACK_FPS,
                                loop=False),
        }
        self.feet = {
            'idle': Animation(load_frames(f'{PLAYER_DIR}/feet/idle', PLAYER_SCALE), PLAYER_FEET_FPS),
            'walk': Animation(load_frames(f'{PLAYER_DIR}/feet/walk', PLAYER_SCALE), PLAYER_FEET_FPS),
        }
        self.pivot = (PLAYER_BODY_PIVOT[0] * PLAYER_SCALE, PLAYER_BODY_PIVOT[1] * PLAYER_SCALE)
        self.moving = False
        self.attacking = False
        self.cooldown = 0.0
        self.attack_count = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in KEY_ATTACK:
            self.attack()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in MOUSE_ATTACK:
            self.attack()

    def attack(self) -> bool:
        if self.attacking or self.cooldown > 0:
            return False
        self.attacking = True
        self.attack_count += 1
        self.body['attack'].reset()
        return True

    def attack_hitbox(self):
        if not self.attacking:
            return None
        first, last = PLAYER_ATTACK_ACTIVE
        if not first <= self.body['attack'].index <= last:
            return None
        return self.attack_area()

    def attack_area(self) -> pygame.Rect:
        center = self.pos + self.facing * PLAYER_ATTACK_REACH
        box = pygame.Rect((0, 0), PLAYER_ATTACK_SIZE)
        box.center = (round(center.x), round(center.y))
        return box

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        direction = Vector2(_pressed(keys, KEY_RIGHT) - _pressed(keys, KEY_LEFT),
                            _pressed(keys, KEY_DOWN) - _pressed(keys, KEY_UP))
        slow = _pressed(keys, KEY_SLOW)
        self.moving = direction.length_squared() > 0
        if self.moving:
            direction.scale_to_length((PLAYER_SLOW_SPEED if slow else PLAYER_SPEED) * dt)
            self.move_and_collide(direction, self.solids)
        self.look_at(pygame.mouse.get_pos())

        feet = self.feet['walk' if self.moving else 'idle']
        feet.fps = PLAYER_FEET_SLOW_FPS if slow else PLAYER_FEET_FPS
        feet.update(dt)

        if self.attacking:
            attack = self.body['attack']
            attack.update(dt)
            if attack.finished:
                self.attacking = False
                self.cooldown = PLAYER_ATTACK_COOLDOWN
        else:
            self.cooldown = max(0.0, self.cooldown - dt)
            self.body['move' if self.moving else 'idle'].update(dt)

    def draw(self, surf: pygame.Surface):
        feet = self.feet['walk' if self.moving else 'idle'].frame
        self.blit_rotated(surf, feet, (feet.get_width() / 2, feet.get_height() / 2))
        if self.attacking:
            body = self.body['attack'].frame
        else:
            body = self.body['move' if self.moving else 'idle'].frame
        self.blit_rotated(surf, body, self.pivot)
