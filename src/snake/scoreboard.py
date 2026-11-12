"""Tela do placar: animação do foguete, câmera, explosões de letras e rolagem. Lógica pura.

Coordenadas em "linhas" do placar (0 = 1º lugar). O tempo entra por `update(dt_ms)` e a
aleatoriedade por um `random.Random` injetado (Princípios I e III).
"""

import random
from dataclasses import dataclass

from snake.highscores import Entry

VISIBLE_ROWS = 5


@dataclass(frozen=True)
class RowView:
    y: float  # linha (fracionária durante a animação)
    entry: Entry
    is_player: bool


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
        self.done = True
        if rank is None:
            self.view_top = float(self._max_top)
        else:
            self.view_top = float(min(max(rank - VISIBLE_ROWS // 2, 0), self._max_top))
        self._events: list[str] = []

    @property
    def _max_top(self) -> int:
        return max(0, len(self.after) - VISIBLE_ROWS)

    def rows(self) -> list[RowView]:
        return [RowView(float(i), e, i == self.rank) for i, e in enumerate(self.after)]

    def update(self, dt_ms: float) -> None:
        pass

    def skip(self) -> None:
        pass

    def scroll(self, direction: int) -> bool:
        """Rola uma linha (-1 sobe, +1 desce) depois da animação; True se a vista mudou."""
        if not self.done:
            return False
        before = self.view_top
        self.view_top = float(min(max(round(self.view_top) + direction, 0), self._max_top))
        return self.view_top != before

    def drain_events(self) -> list[str]:
        events, self._events = self._events, []
        return events
