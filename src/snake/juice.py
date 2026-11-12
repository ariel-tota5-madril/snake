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
PULSE_PEAK_MS, PULSE_PEAK = 60, 1.8
PULSE_DIP_MS, PULSE_DIP = 180, 0.9
COLLISION_SHAKE = (1 / 3, 400)  # (amplitude em casas, duração em ms)
EAT_SHAKE = (1 / 9, 150)  # um terço da colisão (FR-015)
STAMP_SHAKE = (1 / 2, 300)  # 004: impacto de cada palavra da abertura do Frenzy


def ease_out(p: float) -> float:
    """Ease-out cúbico: rápido no começo, suave no fim; p limitado a [0, 1]."""
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def ease_in(p: float) -> float:
    """Ease-in quadrático: começa devagar e chega no máximo no fim (carimbo); p em [0, 1]."""
    p = min(max(p, 0.0), 1.0)
    return p * p


def ease_in_out(p: float) -> float:
    """Ease-in-out suave (cosseno); p limitado a [0, 1]."""
    p = min(max(p, 0.0), 1.0)
    return (1 - math.cos(math.pi * p)) / 2


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    age_ms: float = 0.0
    life_ms: float = PARTICLE_LIFE_MS

    @property
    def life(self) -> float:
        return max(0.0, 1 - self.age_ms / self.life_ms)


class ParticleBurst:
    """Explosão de partículas; `tint` é só um rótulo de cor lido pelo desenho ("fruit", ...)."""

    def __init__(
        self,
        origin: tuple[float, float],
        rng: random.Random,
        count: int = PARTICLES_PER_BURST,
        speed: tuple[float, float] = PARTICLE_SPEED,
        life_ms: float = PARTICLE_LIFE_MS,
        tint: str = "fruit",
    ) -> None:
        self.origin = origin
        self.tint = tint
        self.life_ms = life_ms
        self.particles: list[Particle] = []
        for _ in range(count):
            angle = rng.uniform(0, 2 * math.pi)
            v = rng.uniform(*speed)
            self.particles.append(
                Particle(origin[0], origin[1], math.cos(angle) * v, math.sin(angle) * v, life_ms=life_ms)
            )

    def update(self, dt_ms: float) -> None:
        seconds = dt_ms / 1000
        for p in self.particles:
            p.x += p.vx * seconds
            p.y += p.vy * seconds
            p.age_ms += dt_ms
        self.particles = [p for p in self.particles if p.age_ms < self.life_ms]

    @property
    def done(self) -> bool:
        return not self.particles


class ScorePulse:
    """Pulso "punchy": salta a 1,8x em 60 ms, quica até 0,9x em 180 ms e assenta em 1x em 300 ms."""

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
    def scale(self) -> float:
        t = self._elapsed_ms
        if t is None:
            return 1
        if t <= PULSE_PEAK_MS:
            return lerp(1.0, PULSE_PEAK, ease_out(t / PULSE_PEAK_MS))
        if t <= PULSE_DIP_MS:
            p = (t - PULSE_PEAK_MS) / (PULSE_DIP_MS - PULSE_PEAK_MS)
            return lerp(PULSE_PEAK, PULSE_DIP, ease_in_out(p))
        p = (t - PULSE_DIP_MS) / (PULSE_MS - PULSE_DIP_MS)
        return lerp(PULSE_DIP, 1.0, ease_out(p))

    @property
    def warmth(self) -> float:
        """0 = branco, 1 = amarelo: o flash começa branco e esquenta nos primeiros 60 ms."""
        t = self._elapsed_ms
        return 0 if t is None else min(1.0, t / PULSE_PEAK_MS)

    @property
    def flash(self) -> float:
        """Força do flash sobre a cor normal: 1 no disparo, 0 ao final."""
        t = self._elapsed_ms
        return 0 if t is None else 1 - t / PULSE_MS


class ScreenShake:
    """Tremor com amplitude em casas e decaimento linear; um novo trigger substitui o atual."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self._elapsed_ms: float | None = None
        self._peak = 0.0
        self._duration_ms = 1.0
        self.offset: tuple[float, float] = (0, 0)

    def trigger(self, amplitude: float, duration_ms: float) -> None:
        self._peak = amplitude
        self._duration_ms = duration_ms
        self._elapsed_ms = 0.0
        self.offset = (0, 0)

    @property
    def amplitude(self) -> float:
        if self._elapsed_ms is None:
            return 0.0
        return self._peak * max(0.0, 1 - self._elapsed_ms / self._duration_ms)

    @property
    def done(self) -> bool:
        return self._elapsed_ms is None or self._elapsed_ms >= self._duration_ms

    def update(self, dt_ms: float) -> None:
        if self.done:
            self.offset = (0, 0)
            return
        self._elapsed_ms += dt_ms
        if self.done:
            self.offset = (0, 0)
            return
        a = self.amplitude
        self.offset = (self._rng.uniform(-a, a), self._rng.uniform(-a, a))
