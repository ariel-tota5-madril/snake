"""Catálogo de efeitos, jingles e músicas 8-bit, descritos como notas. Lógica pura.

Todo o áudio é composto aqui e sintetizado por `snake.synth` (FR-001: criado pelo projeto).
"""

from array import array

from snake.flow import SoundEvent
from snake.synth import Note, render

SFX: dict[SoundEvent, tuple[array, float]] = {}
JINGLES: dict[SoundEvent, array] = {}
MUSIC: dict[SoundEvent, array] = {}


def _gameplay_sfx() -> None:
    # (amostras, volume relativo) — volumes de research.md §5; o passo é o mais baixo (FR-002)
    SFX[SoundEvent.STEP] = (render([Note("triangle", 220, 20, decay=1)]), 0.15)
    SFX[SoundEvent.EAT] = (render([Note("square25", 523, 80, freq_end=1046)]), 0.7)
    SFX[SoundEvent.PULSE_POP] = (render([Note("square12", 1568, 40, decay=1)]), 0.5)
    SFX[SoundEvent.CRASH] = (render([Note("noise", 6000, 350, freq_end=700, decay=1)]), 0.9)


def build() -> None:
    """Gera todos os sons (uma vez, ao abrir o jogo)."""
    _gameplay_sfx()
