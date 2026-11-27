from array import array

import pygame
from pygame.math import Vector2

from code.Const import (SFX_GAIN, MIXER_CHANNELS, MUSIC_FADE_MS, VOL_MUSIC, ENEMY_NOISE_RANGE, ENEMY_NOISE_PAN, KEY_MUTE,
                        MSG_MUTED, FONT_NAME, C_GRAY, C_PANEL)


class Audio:
    _ok = None  # None = ainda não tentou iniciar; True/False = resultado da tentativa
    _muted = False
    _sounds = {}
    _music = None  # caminho da música atual
    _font = None

    # ---------- inicialização ----------

    @staticmethod
    def pre_init():
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except pygame.error:
            pass

    @classmethod
    def init(cls) -> bool:
        if cls._ok is None:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.set_num_channels(MIXER_CHANNELS)
                cls._ok = True
            except pygame.error:
                cls._ok = False
        return cls._ok

    @classmethod
    def available(cls) -> bool:
        return cls.init()

    # ---------- mudo ----------

    @classmethod
    def is_muted(cls) -> bool:
        return cls._muted

    @classmethod
    def toggle_mute(cls):
        cls._muted = not cls._muted
        if not cls.available():
            return
        if cls._muted:
            pygame.mixer.stop()  # corta os efeitos que estão tocando
            pygame.mixer.music.set_volume(0)  # a música continua de onde estava ao religar
        else:
            pygame.mixer.music.set_volume(VOL_MUSIC)

    @classmethod
    def handle_event(cls, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key in KEY_MUTE:
            cls.toggle_mute()
            return True
        return False

    @classmethod
    def draw_muted(cls, surf: pygame.Surface, topright: tuple):
        if not cls._muted:
            return
        if cls._font is None:
            cls._font = pygame.font.SysFont(FONT_NAME, 14, bold=True)
        text = cls._font.render(MSG_MUTED, True, C_GRAY)
        rect = text.get_rect(topright=(topright[0] - 6, topright[1] + 4))
        panel = pygame.Surface((rect.width + 12, rect.height + 8), pygame.SRCALPHA)
        panel.fill(C_PANEL)
        surf.blit(panel, panel.get_rect(topright=topright))
        surf.blit(text, rect)

    # ---------- música ----------

    @classmethod
    def play_music(cls, path: str):
        if not cls.available():
            return
        if cls._music == path and pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0 if cls._muted else VOL_MUSIC)
            pygame.mixer.music.play(-1)
            cls._music = path
        except pygame.error:
            cls._music = None

    @classmethod
    def stop_music(cls, fade_ms: int = MUSIC_FADE_MS):
        if not cls.available():
            return
        pygame.mixer.music.fadeout(fade_ms)
        cls._music = None

    # ---------- efeitos ----------

    @classmethod
    def sound(cls, path: str):
        if not cls.available():
            return None
        if path not in cls._sounds:
            try:
                snd = pygame.mixer.Sound(path)
                gain = SFX_GAIN.get(path, 1.0)
                cls._sounds[path] = cls._amplify(snd, gain) if gain != 1.0 else snd
            except (pygame.error, FileNotFoundError):
                cls._sounds[path] = None
        return cls._sounds[path]

    @staticmethod
    def _amplify(snd, gain: float):
        # set_volume não passa de 1.0; para ganho maior multiplica as amostras (16 bits) uma vez, com corte
        if pygame.mixer.get_init()[1] != -16:
            return snd
        samples = array('h', snd.get_raw())
        for i, value in enumerate(samples):
            samples[i] = max(-32768, min(32767, round(value * gain)))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    @classmethod
    def play(cls, path: str, volume: float = 1.0):
        if cls._muted:
            return None
        snd = cls.sound(path)
        if snd is None:
            return None
        snd.set_volume(volume)
        return snd.play()

    @classmethod
    def play_at(cls, path: str, volume: float, source, listener):
        delta = Vector2(source) - Vector2(listener)
        distance = delta.length()
        if distance >= ENEMY_NOISE_RANGE:
            return None
        level = volume * (1 - distance / ENEMY_NOISE_RANGE)
        pan = max(-1.0, min(1.0, delta.x / ENEMY_NOISE_RANGE * 2)) * ENEMY_NOISE_PAN
        channel = cls.play(path, 1.0)
        if channel is not None:
            channel.set_volume(level * min(1.0, 1 - pan), level * min(1.0, 1 + pan))
        return channel

    @staticmethod
    def stop(channel):
        if channel is not None:
            channel.stop()
