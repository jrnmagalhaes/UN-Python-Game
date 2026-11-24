import pygame


class Animation:
    def __init__(self, frames: list, fps: float, loop: bool = True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.time = 0.0
        self.index = 0
        self.finished = False

    def reset(self):
        self.time = 0.0
        self.index = 0
        self.finished = False

    def update(self, dt: float):
        if self.finished:
            return
        self.time += dt
        index = int(self.time * self.fps)
        if index >= len(self.frames):
            if self.loop:
                self.time %= len(self.frames) / self.fps
                index = int(self.time * self.fps) % len(self.frames)
            else:
                index = len(self.frames) - 1
                self.finished = True
        self.index = index

    @property
    def frame(self) -> pygame.Surface:
        return self.frames[self.index]
