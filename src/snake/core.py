"""Núcleo puro do Snake: regras de jogo sem renderização, sem relógio e sem RNG global."""

import random
from enum import Enum

Cell = tuple[int, int]
INPUT_BUFFER = 2  # comandos guardados: sequências rápidas (ex.: meia-volta) não se perdem


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
        self.restart()

    def restart(self) -> None:
        """Volta ao estado inicial (FR-002) mantendo o mesmo RNG, para a sessão ser reproduzível."""
        cx, cy = self.width // 2, self.height // 2
        self._snake: list[Cell] = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = Direction.RIGHT
        self._queue: list[Direction] = []  # input buffer: um comando consumido por passo
        self.food: Cell | None = None
        self.specials: dict[Cell, int] = {}  # Feeding Frenzy: casa -> variante (0 roxa, 1 dourada)
        self._in_frenzy = False
        self.score = 0
        self.status = Status.RUNNING
        self.food = self._spawn_food()

    @property
    def snake(self) -> tuple[Cell, ...]:
        return tuple(self._snake)

    @property
    def in_frenzy(self) -> bool:
        return self._in_frenzy

    def _free_cells(self) -> list[Cell]:
        """Casas livres em ordem fixa: o sorteio fica reproduzível pela seed."""
        occupied = set(self._snake) | set(self.specials)
        return [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]

    def _spawn_food(self) -> Cell | None:
        free = self._free_cells()
        return self._rng.choice(free) if free else None

    def start_frenzy(self, count: int = 10) -> int:
        """Troca a fruta normal por até `count` frutas especiais; devolve quantas surgiram."""
        food, self.food = self.food, None
        free = self._free_cells()
        if not free:
            self.food = food
            return 0
        cells = self._rng.sample(free, min(count, len(free)))
        self.specials = {cell: i % 2 for i, cell in enumerate(cells)}
        self._in_frenzy = True
        return len(cells)

    def end_frenzy(self) -> None:
        """Fim do Frenzy: some com as especiais e volta uma fruta normal."""
        self.specials = {}
        self._in_frenzy = False
        self.food = self._spawn_food()

    def fail(self) -> None:
        """Derrota sem colisão (tempo do Frenzy esgotado)."""
        self.status = Status.GAME_OVER

    def turn(self, direction: Direction) -> None:
        """Enfileira uma direção (até INPUT_BUFFER); cada passo aplica a próxima da fila.

        A validação é contra a última direção da fila (ou a atual, se vazia): o oposto seria
        meia-volta sobre o corpo e a repetida não muda nada, então ambos são ignorados.
        """
        if self.status is not Status.RUNNING or len(self._queue) >= INPUT_BUFFER:
            return
        last = self._queue[-1] if self._queue else self.direction
        if direction is last or direction is last.opposite:
            return
        self._queue.append(direction)

    def step(self) -> None:
        """Avança um passo de jogo (ordem descrita em data-model.md)."""
        if self.status is not Status.RUNNING:
            return
        if self._queue:
            self.direction = self._queue.pop(0)

        hx, hy = self._snake[0]
        dx, dy = self.direction.value
        head = (hx + dx, hy + dy)

        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.status = Status.GAME_OVER
            return
        eating = head == self.food
        body = self._snake if eating else self._snake[:-1]
        if head in body:
            self.status = Status.GAME_OVER
            return

        self._snake.insert(0, head)
        if not eating:
            self._snake.pop()
            self.specials.pop(head, None)  # especial: some sem crescer nem pontuar
            return

        self.score += 1
        self.food = self._spawn_food()
        if self.food is None:
            self.status = Status.WON
