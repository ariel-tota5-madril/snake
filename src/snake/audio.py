"""Adaptador de áudio: o único módulo que usa pygame.mixer.

Toca os eventos sonoros que o `Flow` emite. Se o mixer não abrir (sem dispositivo de áudio), o
jogo segue em silêncio com `SilentAudio` (FR-013).
"""

import pygame

from snake import sounds
from snake.flow import SoundEvent
from snake.synth import SAMPLE_RATE

CHANNELS = 16
MUSIC_GAIN = 0.5  # música abaixo dos efeitos (FR-011)
PAUSE_DUCK = 0.35  # música ainda mais baixa na pausa (FR-015)
DEFAULT_MUSIC, DEFAULT_SFX = 60, 80


def pre_init() -> None:
    """Deve ser chamado antes de pygame.init(): mono, 16 bits, buffer curto (~23 ms, SC-001)."""
    pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)


class SilentAudio:
    """Mesma interface do Audio, sem som."""

    def play(self, event: SoundEvent) -> None:
        pass

    def apply_volumes(self, settings) -> None:
        pass


class Audio:
    def __init__(self, settings) -> None:
        pygame.mixer.set_num_channels(CHANNELS)
        pygame.mixer.set_reserved(1)
        self._music_channel = pygame.mixer.Channel(0)
        sounds.build()
        self._sfx = {e: (pygame.mixer.Sound(buffer=s.tobytes()), rel) for e, (s, rel) in sounds.SFX.items()}
        self._jingles = {e: pygame.mixer.Sound(buffer=s.tobytes()) for e, s in sounds.JINGLES.items()}
        self._music = {e: pygame.mixer.Sound(buffer=s.tobytes()) for e, s in sounds.MUSIC.items()}
        self._music_volume = DEFAULT_MUSIC / 100
        self._sfx_volume = DEFAULT_SFX / 100
        self._ducked = False
        self.apply_volumes(settings)

    @classmethod
    def create(cls, settings=None) -> "Audio | SilentAudio":
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return cls(settings)
        except pygame.error:
            return SilentAudio()

    def apply_volumes(self, settings) -> None:
        if settings is not None:
            self._music_volume = settings.music / 100
            self._sfx_volume = settings.sfx / 100
        self._update_music_volume()

    def _update_music_volume(self) -> None:
        duck = PAUSE_DUCK if self._ducked else 1.0
        self._music_channel.set_volume(MUSIC_GAIN * self._music_volume * duck)

    def play(self, event: SoundEvent) -> None:
        if event in self._music:
            self._ducked = False
            self._update_music_volume()
            self._music_channel.play(self._music[event], loops=-1)
        elif event is SoundEvent.MUSIC_STOP:
            self._music_channel.stop()
        elif event in (SoundEvent.MUSIC_DUCK, SoundEvent.MUSIC_UNDUCK):
            self._ducked = event is SoundEvent.MUSIC_DUCK
            self._update_music_volume()
        elif event in self._jingles:
            channel = self._jingles[event].play()
            if channel is not None:
                channel.set_volume(self._sfx_volume)
        elif event in self._sfx:
            sound, relative = self._sfx[event]
            channel = sound.play()
            if channel is not None:
                channel.set_volume(relative * self._sfx_volume)
