"""Efeitos visuais (partículas, pulso do placar, tremor): lógica pura, sem Pygame nem relógio.

Todo tempo entra por `update(dt_ms)`; toda aleatoriedade vem de um `random.Random` injetado.
"""

import math
import random
from dataclasses import dataclass

PARTICLE_LIFE_MS = 600
PARTICLES_PER_BURST = 16
PARTICLE_SPEED = (2.5, 7.5)  # casas por segundo
PULSE_MS = 300
PULSE_GROWTH = 0.5


def ease_out(p: float) -> float:
    """Ease-out cúbico: rápido no começo, suave no fim; p limitado a [0, 1]."""
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    age_ms: float = 0.0

    @property
    def life(self) -> float:
        return max(0.0, 1 - self.age_ms / PARTICLE_LIFE_MS)


class ParticleBurst:
    def __init__(self, origin: tuple[float, float], rng: random.Random) -> None:
        self.origin = origin
        self.particles: list[Particle] = []
        for _ in range(PARTICLES_PER_BURST):
            angle = rng.uniform(0, 2 * math.pi)
            speed = rng.uniform(*PARTICLE_SPEED)
            self.particles.append(
                Particle(origin[0], origin[1], math.cos(angle) * speed, math.sin(angle) * speed)
            )

    def update(self, dt_ms: float) -> None:
        seconds = dt_ms / 1000
        for p in self.particles:
            p.x += p.vx * seconds
            p.y += p.vy * seconds
            p.age_ms += dt_ms
        self.particles = [p for p in self.particles if p.age_ms < PARTICLE_LIFE_MS]

    @property
    def done(self) -> bool:
        return not self.particles


class ScorePulse:
    def __init__(self) -> None:
        self._elapsed_ms: float | None = None

    def trigger(self) -> None:
        self._elapsed_ms = 0.0

    def update(self, dt_ms: float) -> None:
        if self._elapsed_ms is None:
            return
        self._elapsed_ms += dt_ms
        if self._elapsed_ms >= PULSE_MS:
            self._elapsed_ms = None

    @property
    def _progress(self) -> float | None:
        return None if self._elapsed_ms is None else self._elapsed_ms / PULSE_MS

    @property
    def scale(self) -> float:
        p = self._progress
        return 1 if p is None else 1 + PULSE_GROWTH * math.sin(math.pi * p)

    @property
    def flash(self) -> float:
        p = self._progress
        return 0 if p is None else 1 - p
