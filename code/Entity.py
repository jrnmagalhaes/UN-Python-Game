from abc import ABC, abstractmethod

import pygame
from pygame.math import Vector2


class Entity(ABC):
    def __init__(self, pos, hitbox_size: tuple, angle: float = 0.0):
        self.pos = Vector2(pos)
        self.angle = angle
        self.hitbox = pygame.Rect((0, 0), hitbox_size)
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))

    @property
    def rect(self) -> pygame.Rect:
        return self.hitbox

    @property
    def facing(self) -> Vector2:
        return Vector2(1, 0).rotate(-self.angle)

    def look_at(self, target):
        delta = Vector2(target) - self.pos
        if delta.length_squared() > 1:
            self.angle = -delta.as_polar()[1]

    def move_and_collide(self, delta: Vector2, solids: list):
        if delta.x:
            self.pos.x += delta.x
            self.hitbox.centerx = round(self.pos.x)
            for wall in solids:
                if self.hitbox.colliderect(wall):
                    if delta.x > 0:
                        self.hitbox.right = wall.left
                    else:
                        self.hitbox.left = wall.right
                    self.pos.x = self.hitbox.centerx
        if delta.y:
            self.pos.y += delta.y
            self.hitbox.centery = round(self.pos.y)
            for wall in solids:
                if self.hitbox.colliderect(wall):
                    if delta.y > 0:
                        self.hitbox.bottom = wall.top
                    else:
                        self.hitbox.top = wall.bottom
                    self.pos.y = self.hitbox.centery

    def blit_rotated(self, surf: pygame.Surface, image: pygame.Surface, pivot: tuple):
        offset = Vector2(image.get_width() / 2 - pivot[0], image.get_height() / 2 - pivot[1])
        rotated = pygame.transform.rotozoom(image, self.angle, 1)
        center = self.pos + offset.rotate(-self.angle)
        surf.blit(rotated, rotated.get_rect(center=(round(center.x), round(center.y))))

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, surf: pygame.Surface):
        pass
