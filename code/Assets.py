import os
import re

import pygame

_frames_cache = {}
_number_re = re.compile(r'(\d+)(?=\.[^.]+$)')


def _frame_number(name: str) -> int:
    match = _number_re.search(name)
    return int(match.group(1)) if match else -1


def load_frames(folder: str, scale: float = 1.0, prefix: str = '') -> list:
    key = (folder, scale, prefix)
    if key not in _frames_cache:
        names = sorted((n for n in os.listdir(folder) if n.startswith(prefix) and n.lower().endswith('.png')),
                       key=_frame_number)
        frames = []
        for name in names:
            img = pygame.image.load(f'{folder}/{name}').convert_alpha()
            if scale != 1.0:
                w, h = img.get_size()
                img = pygame.transform.smoothscale(img, (max(1, round(w * scale)), max(1, round(h * scale))))
            frames.append(img)
        if not frames:
            raise FileNotFoundError(f'Nenhum frame encontrado em {folder}/{prefix}*')
        _frames_cache[key] = frames
    return _frames_cache[key]
