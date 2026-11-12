"""Núcleo puro do Snake: regras de jogo sem renderização, sem relógio e sem RNG global."""

import random
from enum import Enum

Cell = tuple[int, int]


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def opposite(self) -> "Direction":
        dx, dy = self.value
        return Direction((-dx, -dy))


class Status(Enum):
    RUNNING = "running"
    GAME_OVER = "game_over"
    WON = "won"


class Game:
    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        rng: random.Random | None = None,
        seed: int | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self._rng = rng if rng is not None else random.Random(seed)
        cx, cy = width // 2, height // 2
        self._snake: list[Cell] = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = Direction.RIGHT
        self._pending: Direction | None = None
        self.food: Cell | None = None
        self.score = 0
        self.status = Status.RUNNING

    @property
    def snake(self) -> tuple[Cell, ...]:
        return tuple(self._snake)

    def turn(self, direction: Direction) -> None:
        """Registra a direção do próximo passo (no máximo um comando válido por passo)."""
        if self.status is not Status.RUNNING or self._pending is not None:
            return
        if direction is self.direction.opposite:
            return
        self._pending = direction

    def step(self) -> None:
        """Avança um passo de jogo (ordem descrita em data-model.md)."""
        if self.status is not Status.RUNNING:
            return
        if self._pending is not None:
            self.direction = self._pending
            self._pending = None

        hx, hy = self._snake[0]
        dx, dy = self.direction.value
        head = (hx + dx, hy + dy)

        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.status = Status.GAME_OVER
            return
        if head in self._snake[:-1]:
            self.status = Status.GAME_OVER
            return

        self._snake.insert(0, head)
        self._snake.pop()
