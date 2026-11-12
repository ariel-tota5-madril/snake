"""Tela do placar: animação do foguete, câmera, explosões de letras e rolagem. Lógica pura.

Coordenadas em "linhas" do placar (0 = 1º lugar). O tempo entra por `update(dt_ms)` e a
aleatoriedade por um `random.Random` injetado (Princípios I e III). Linha do tempo em
specs/005-highscore-table/research.md §4.
"""

import math
import random
from dataclasses import dataclass
from enum import Enum

from snake.highscores import CAPACITY, Entry
from snake.juice import ParticleBurst, ease_in_out, ease_out, lerp

VISIBLE_ROWS = 5
IGNITION_MS = 700
LAND_MS = 300
FIRST_PLACE_MS = 1000
FIRST_POP_MS = 300
V_MAX = 5.0  # linhas por segundo
ACCEL_DIST = 1.5  # linhas até atingir V_MAX
ACCEL = V_MAX**2 / (2 * ACCEL_DIST)
FOLLOW_AT = 1.6  # posição na tela (linhas a partir do topo) em que a câmera passa a seguir
JITTER = 0.08  # tremor da ignição, em linhas
FLAME_EVERY_MS = 40
FLAME_ANGLE = (math.pi / 2 - 0.5, math.pi / 2 + 0.5)  # para baixo
SCATTER_MS, REFORM_MS = 300, 350
FALL_MS, GRAVITY = 800, 12.0
SHATTER_SPEED = (2.0, 6.0)


class ScorePhase(Enum):
    IGNITION = "ignition"
    CLIMB = "climb"
    LANDING = "landing"
    FIRST_PLACE = "first_place"
    DONE = "done"


@dataclass(frozen=True)
class RowView:
    y: float  # linha (fracionária durante a animação)
    entry: Entry
    is_player: bool


class Shatter:
    """Letras de uma linha espalhando; remontam em `to_y` ou, se `to_y` é None, caem para fora."""

    def __init__(self, entry: Entry, from_y: float, to_y: float | None, rng: random.Random) -> None:
        self.entry = entry
        self.from_y = from_y
        self.to_y = to_y
        self._t = 0.0
        self._velocity = []
        for _ in range(len(entry.name) + len(str(entry.score))):
            a = rng.uniform(0, 2 * math.pi)
            v = rng.uniform(*SHATTER_SPEED)
            self._velocity.append((math.cos(a) * v, math.sin(a) * v))

    def update(self, dt_ms: float) -> None:
        self._t += dt_ms

    @property
    def _reform(self) -> float:
        return ease_in_out((self._t - SCATTER_MS) / REFORM_MS) if self._t > SCATTER_MS else 0.0

    def offsets(self) -> list[tuple[float, float]]:
        if self.to_y is None:  # expulso: voa e cai
            s = min(self._t, FALL_MS) / 1000
            return [(vx * s, vy * s + GRAVITY * s * s / 2) for vx, vy in self._velocity]
        spread = ease_out(self._t / SCATTER_MS) * SCATTER_MS / 1000
        keep = 1 - self._reform
        return [(vx * spread * keep, vy * spread * keep) for vx, vy in self._velocity]

    @property
    def base_y(self) -> float:
        if self.to_y is None:
            return self.from_y
        return lerp(self.from_y, self.to_y, self._reform)

    @property
    def alpha(self) -> float:
        if self.to_y is None:
            return max(0.0, 1 - self._t / FALL_MS)
        return 1.0

    @property
    def done(self) -> bool:
        return self._t >= (FALL_MS if self.to_y is None else SCATTER_MS + REFORM_MS)


class Scoreboard:
    def __init__(
        self,
        before: list[Entry],
        after: list[Entry],
        rank: int | None,
        player: Entry,
        rng: random.Random,
    ) -> None:
        self.before = list(before)
        self.after = list(after)
        self.rank = rank
        self.player = player
        self._rng = rng
        self.outside = player if rank is None else None
        self.shatters: list[Shatter] = []
        self.bursts: list[ParticleBurst] = []
        self.rocket_offset: tuple[float, float] = (0.0, 0.0)
        self.first_place = 0.0
        self._events: list[str] = []
        self._hit: set[int] = set()  # linhas antigas já atingidas
        self._shatter_of: dict[int, Shatter] = {}
        self._t = 0.0  # tempo na etapa atual
        self._flame_ms = 0.0
        self._started = False
        self._y0 = len(self.after) - 1  # chão da lista
        self.view_top = float(self._max_top)
        if rank is None:
            self.phase = ScorePhase.DONE
            self.rocket_y: float | None = None
        else:
            self.phase = ScorePhase.IGNITION
            self.rocket_y = float(self._y0)

    # --- consultas ------------------------------------------------------------------------

    @property
    def done(self) -> bool:
        return self.phase is ScorePhase.DONE

    @property
    def _max_top(self) -> int:
        return max(0, len(self.after) - VISIBLE_ROWS)

    @property
    def _distance(self) -> float:
        return float(self._y0 - self.rank)

    def rows(self) -> list[RowView]:
        """Linhas estáticas a desenhar (as que estão explodindo vêm em `shatters`)."""
        rows = []
        for i, entry in enumerate(self.after):
            if i == self.rank:
                rows.append(RowView(self.rocket_y if not self.done else float(i), entry, True))
                continue
            if self.rank is not None and i > self.rank:
                old = i - 1  # empurrada uma linha para baixo pelo foguete
                if old not in self._hit:
                    rows.append(RowView(float(old), entry, False))
                elif old not in self._shatter_of or self._shatter_of[old].done:
                    rows.append(RowView(float(i), entry, False))
                continue
            rows.append(RowView(float(i), entry, False))
        return rows

    def drain_events(self) -> list[str]:
        events, self._events = self._events, []
        return events

    # --- tempo ----------------------------------------------------------------------------

    def update(self, dt_ms: float) -> None:
        for sh in self.shatters:
            sh.update(dt_ms)
        self.shatters = [sh for sh in self.shatters if not sh.done]
        for burst in self.bursts:
            burst.update(dt_ms)
        self.bursts = [b for b in self.bursts if not b.done]
        if self.done:
            return
        if not self._started:
            self._start()
        self._t += dt_ms
        if self.phase is ScorePhase.IGNITION:
            self._ignition()
        elif self.phase is ScorePhase.CLIMB:
            self._climb()
        elif self.phase is ScorePhase.LANDING:
            if self._t >= LAND_MS and not self.shatters:
                if self.rank == 0:
                    self._events.append("first")
                    self._enter(ScorePhase.FIRST_PLACE)
                else:
                    self._enter(ScorePhase.DONE)
        elif self.phase is ScorePhase.FIRST_PLACE:
            self.first_place = ease_out(self._t / FIRST_POP_MS)
            if self._t >= FIRST_PLACE_MS:
                self.first_place = 1.0
                self._enter(ScorePhase.DONE)
        if self.phase in (ScorePhase.IGNITION, ScorePhase.CLIMB):
            self._flame(dt_ms)

    def _start(self) -> None:
        self._started = True
        self._events.append("ignite")
        if len(self.before) >= CAPACITY:  # placar cheio: o antigo 10º explode e cai (FR-013a)
            self._events.append("hit")
            self.shatters.append(Shatter(self.before[-1], float(self._y0), None, self._rng))

    def _ignition(self) -> None:
        self.rocket_offset = (self._rng.uniform(-JITTER, JITTER), self._rng.uniform(-JITTER, JITTER))
        if self._t >= IGNITION_MS:
            self.rocket_offset = (0.0, 0.0)
            if self._distance > 0:
                self._events.append("launch")
                self._enter(ScorePhase.CLIMB)
            else:
                self._land()

    def _climb(self) -> None:
        t = self._t / 1000
        t_acc = V_MAX / ACCEL
        travelled = ACCEL * t * t / 2 if t < t_acc else ACCEL_DIST + V_MAX * (t - t_acc)
        travelled = min(travelled, self._distance)
        self.rocket_y = self._y0 - travelled
        self.view_top = self._camera(self.rocket_y)
        for old in range(self._y0 - 1, self.rank - 1, -1):  # bate nos nomes que passou
            if old not in self._hit and self.rocket_y <= old + 0.5:
                self._hit.add(old)
                self._events.append("hit")
                shatter = Shatter(self.before[old], float(old), float(old + 1), self._rng)
                self._shatter_of[old] = shatter
                self.shatters.append(shatter)
        if travelled >= self._distance:
            self._land()

    def _camera(self, y: float) -> float:
        """A lista desce para manter o foguete em FOLLOW_AT; para quando o 1º lugar cabe na tela."""
        return min(max(min(float(self._max_top), y - FOLLOW_AT), 0.0), float(self._max_top))

    def _land(self) -> None:
        self.rocket_y = float(self.rank)
        self._events.append("land")
        self._enter(ScorePhase.LANDING)

    def _flame(self, dt_ms: float) -> None:
        self._flame_ms += dt_ms
        while self._flame_ms >= FLAME_EVERY_MS:
            self._flame_ms -= FLAME_EVERY_MS
            self.bursts.append(
                ParticleBurst(
                    (0.0, self.rocket_y + 0.4),
                    self._rng,
                    count=5,
                    speed=(2, 5),
                    life_ms=350,
                    tint="flame",
                    angle=FLAME_ANGLE,
                )
            )

    def _enter(self, phase: ScorePhase) -> None:
        self.phase = phase
        self._t = 0.0

    # --- entradas -------------------------------------------------------------------------

    def skip(self) -> None:
        """Enter: vai direto ao estado final, sem eventos (FR-015)."""
        if self.done:
            return
        self._started = True
        self.rocket_y = float(self.rank)
        self.view_top = self._camera(float(self.rank))
        self._hit = set(range(self.rank, self._y0))
        self._shatter_of = {}
        self.shatters = []
        self.bursts = []
        self.rocket_offset = (0.0, 0.0)
        self.first_place = 1.0 if self.rank == 0 else 0.0
        self._events = []
        self._enter(ScorePhase.DONE)

    def scroll(self, direction: int) -> bool:
        """Rola uma linha (-1 sobe, +1 desce) depois da animação; True se a vista mudou."""
        if not self.done:
            return False
        before = self.view_top
        self.view_top = float(min(max(round(self.view_top) + direction, 0), self._max_top))
        return self.view_top != before
