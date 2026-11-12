"""Catálogo de efeitos, jingles e músicas 8-bit, descritos como notas. Lógica pura.

Todo o áudio é composto aqui e sintetizado por `snake.synth` (FR-001: criado pelo projeto).
"""

from array import array

from snake.flow import SoundEvent

SFX: dict[SoundEvent, tuple[array, float]] = {}
JINGLES: dict[SoundEvent, array] = {}
MUSIC: dict[SoundEvent, array] = {}


def build() -> None:
    """Gera todos os sons (uma vez, ao abrir o jogo)."""
