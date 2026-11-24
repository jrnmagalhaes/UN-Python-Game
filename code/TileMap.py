import pygame

from code.Const import (TILE_SIZE, MAP_COLS, MAP_ROWS, MAP_OFFSET, TILE_DIR, IMG_WALL, IMG_TABLE, IMG_PLANT,
                        TILE_WALL, TILE_PLAYER, TILE_TABLE, TILE_PLANT, TILE_SOLID, C_WALL_EDGE, C_SHADOW)
from code.LevelData import ENEMY_PAUSE_DEFAULT


class TileMap:
    _image_cache = {}

    def __init__(self, level_data: dict):
        self.grid = level_data['grid']
        self._validate(level_data)
        self.rect = pygame.Rect(MAP_OFFSET, (MAP_COLS * TILE_SIZE, MAP_ROWS * TILE_SIZE))
        self.player_start = (0, 0)
        self.solid_rects = []
        self.surface = self._render(level_data['floor'], level_data.get('floor_tint'))
        self.enemies = [{'route': [self.tile_center(c, r) for c, r in e['route']],
                         'loop': e.get('loop', False),
                         'pause': e.get('pause', ENEMY_PAUSE_DEFAULT)}
                        for e in level_data['enemies']]

    @staticmethod
    def tile_center(col: int, row: int) -> tuple:
        return (MAP_OFFSET[0] + col * TILE_SIZE + TILE_SIZE // 2,
                MAP_OFFSET[1] + row * TILE_SIZE + TILE_SIZE // 2)

    @staticmethod
    def tile_rect(col: int, row: int) -> pygame.Rect:
        return pygame.Rect(MAP_OFFSET[0] + col * TILE_SIZE, MAP_OFFSET[1] + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def is_solid(self, col: int, row: int) -> bool:
        if not (0 <= col < MAP_COLS and 0 <= row < MAP_ROWS):
            return True
        return self.grid[row][col] in TILE_SOLID

    @classmethod
    def _image(cls, path: str, size: int) -> pygame.Surface:
        key = (path, size)
        if key not in cls._image_cache:
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            k = size / max(w, h)
            cls._image_cache[key] = pygame.transform.smoothscale(img, (round(w * k), round(h * k)))
        return cls._image_cache[key]

    def _render(self, floor_name: str, floor_tint=None) -> pygame.Surface:
        surf = pygame.Surface(self.rect.size, depth=24)
        floor = self._image(f'{TILE_DIR}/Walls/{floor_name}', TILE_SIZE)
        if floor_tint:
            floor = floor.copy()
            floor.fill(floor_tint, special_flags=pygame.BLEND_RGB_MULT)
        wall = self._image(IMG_WALL, TILE_SIZE)
        props = {TILE_TABLE: self._image(IMG_TABLE, TILE_SIZE - 4),
                 TILE_PLANT: self._image(IMG_PLANT, TILE_SIZE)}
        shadow = pygame.Surface((TILE_SIZE, TILE_SIZE // 4), pygame.SRCALPHA)
        shadow.fill(C_SHADOW)
        shadow_v = pygame.transform.rotate(shadow, 90)

        for row, line in enumerate(self.grid):
            for col, ch in enumerate(line):
                pos = (col * TILE_SIZE, row * TILE_SIZE)
                if ch == TILE_WALL:
                    surf.blit(wall, pos)
                    continue
                surf.blit(floor, pos)
                if self.grid[row - 1][col] == TILE_WALL:
                    surf.blit(shadow, pos)
                if self.grid[row][col - 1] == TILE_WALL:
                    surf.blit(shadow_v, pos)
                if ch in props:
                    img = props[ch]
                    surf.blit(img, img.get_rect(center=(pos[0] + TILE_SIZE // 2, pos[1] + TILE_SIZE // 2)))
                elif ch == TILE_PLAYER:
                    self.player_start = self.tile_center(col, row)

        for row, line in enumerate(self.grid):
            for col, ch in enumerate(line):
                if ch != TILE_WALL:
                    continue
                x, y = col * TILE_SIZE, row * TILE_SIZE
                edges = (((0, -1), (x, y), (x + TILE_SIZE - 1, y)),
                         ((0, 1), (x, y + TILE_SIZE - 1), (x + TILE_SIZE - 1, y + TILE_SIZE - 1)),
                         ((-1, 0), (x, y), (x, y + TILE_SIZE - 1)),
                         ((1, 0), (x + TILE_SIZE - 1, y), (x + TILE_SIZE - 1, y + TILE_SIZE - 1)))
                for (dc, dr), a, b in edges:
                    if not self.is_solid(col + dc, row + dr) or self._is_prop(col + dc, row + dr):
                        pygame.draw.line(surf, C_WALL_EDGE, a, b, 2)

        self.solid_rects = self._build_solid_rects()
        return surf.convert()

    def _is_prop(self, col: int, row: int) -> bool:
        return 0 <= col < MAP_COLS and 0 <= row < MAP_ROWS and self.grid[row][col] in (TILE_TABLE, TILE_PLANT)

    def _build_solid_rects(self) -> list:
        rects = []
        for row, line in enumerate(self.grid):
            col = 0
            while col < MAP_COLS:
                if line[col] in TILE_SOLID:
                    start = col
                    while col < MAP_COLS and line[col] in TILE_SOLID:
                        col += 1
                    r = self.tile_rect(start, row)
                    r.width = (col - start) * TILE_SIZE
                    rects.append(r)
                else:
                    col += 1
        return rects

    def _validate(self, data: dict):
        name = data.get('name', '?')
        assert len(self.grid) == MAP_ROWS, f'{name}: {len(self.grid)} linhas (esperado {MAP_ROWS})'
        for r, line in enumerate(self.grid):
            assert len(line) == MAP_COLS, f'{name}: linha {r} tem {len(line)} colunas (esperado {MAP_COLS})'
        assert sum(line.count(TILE_PLAYER) for line in self.grid) == 1, f'{name}: precisa de exatamente um P'
        for i, enemy in enumerate(data['enemies']):
            route = enemy['route']
            points = route + [route[0]] if enemy.get('loop') else route
            for (c1, r1), (c2, r2) in zip(points, points[1:]):
                assert c1 == c2 or r1 == r2, f'{name}: inimigo {i} tem segmento diagonal {(c1, r1)}->{(c2, r2)}'
                for c in range(min(c1, c2), max(c1, c2) + 1):
                    for r in range(min(r1, r2), max(r1, r2) + 1):
                        assert not self.is_solid(c, r), f'{name}: rota do inimigo {i} atravessa obstáculo em {(c, r)}'
