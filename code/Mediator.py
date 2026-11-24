from pygame.math import Vector2

from code.Const import VIEW_RANGE, VIEW_FOV, BACKSTAB_ANGLE
from code.Enemy import Enemy
from code.Player import Player


class Mediator:
    @staticmethod
    def angle_to(enemy: Enemy, point) -> float:
        delta = Vector2(point) - enemy.pos
        if delta.length_squared() < 1:
            return 0.0
        return abs((enemy.facing.angle_to(delta) + 180) % 360 - 180)

    @staticmethod
    def can_see(enemy: Enemy, player: Player) -> bool:
        if not enemy.alive:
            return False
        if enemy.pos.distance_to(player.pos) > VIEW_RANGE:
            return False
        return Mediator.angle_to(enemy, player.pos) <= VIEW_FOV / 2

    @staticmethod
    def is_behind(enemy: Enemy, player: Player) -> bool:
        return Mediator.angle_to(enemy, player.pos) > BACKSTAB_ANGLE

    @staticmethod
    def find_watcher(player: Player, enemies: list):
        for enemy in enemies:
            if Mediator.can_see(enemy, player):
                return enemy
        return None

    @staticmethod
    def resolve_attack(player: Player, enemies: list) -> tuple:
        hitbox = player.attack_hitbox()
        killed, blocked = [], []
        if hitbox is None:
            return killed, blocked
        for enemy in enemies:
            if not enemy.alive or enemy.last_hit_attack == player.attack_count:
                continue
            if not hitbox.colliderect(enemy.hitbox):
                continue
            enemy.last_hit_attack = player.attack_count
            if Mediator.is_behind(enemy, player):
                enemy.kill()
                killed.append(enemy)
            else:
                blocked.append(enemy)
        return killed, blocked
