# Contract: `snake.highscores`, `snake.scoreboard`, `snake.menu.NameEntry`

Todos puros: sem `pygame`, `time` ou `datetime`.

## `snake.highscores`

```python
CAPACITY = 10
NAME_MAX = 10

@dataclass(frozen=True)
class Entry:
    name: str
    score: int

class Highscores:
    entries: list[Entry]
    def __init__(self, entries: list[Entry] | None = None) -> None: ...
    def rank_for(self, score: int) -> int | None: ...
    def insert(self, name: str, score: int) -> int | None: ...
    @classmethod
    def load(cls, path) -> "Highscores": ...   # nunca levanta exceção por arquivo ruim
    def save(self, path) -> None: ...          # cria a pasta
```

Garantias: `len(entries) <= 10`; ordem decrescente; empate → mais antigo acima; `load(save(x))`
devolve as mesmas entradas.

## `snake.menu.NameEntry`

```python
class NameEntry:
    text: str
    def __init__(self, initial: str = "") -> None: ...
    def type(self, ch: str) -> bool: ...       # True se o texto mudou
    def backspace(self) -> bool: ...
    @property
    def value(self) -> str: ...                # sem espaços nas pontas
    @property
    def confirmable(self) -> bool: ...
```

## `snake.scoreboard`

```python
VISIBLE_ROWS = 5

class Scoreboard:
    def __init__(self, before: list[Entry], after: list[Entry], rank: int | None,
                 player: Entry, rng: random.Random) -> None: ...
    phase: ScorePhase
    done: bool
    rocket_y: float | None
    rocket_offset: tuple[float, float]
    view_top: float
    shatters: list[Shatter]
    bursts: list[ParticleBurst]
    first_place: float
    outside: Entry | None
    def rows(self) -> list[RowView]: ...
    def update(self, dt_ms: float) -> None: ...
    def skip(self) -> None: ...
    def scroll(self, direction: int) -> bool: ...   # -1 sobe, +1 desce; só em DONE
    def drain_events(self) -> list[str]: ...
```

Garantias: animação total ≤ 5 s; mesma seed → mesmos deslocamentos e partículas; `skip()` leva ao
mesmo estado final que `update` até o fim (posições, câmera, `first_place`), sem eventos extras.

## `snake.juice` — delta

`ParticleBurst(..., angle: tuple[float, float] = (0, 2π))`: faixa de ângulos (radianos, y para
baixo) das partículas; padrão inalterado.

## Revisão pós-clarificação

```python
class Scoreboard:
    @classmethod
    def viewer(cls, entries: list[Entry], rng: random.Random) -> "Scoreboard": ...
    def empty_slots(self) -> list[int]: ...

@dataclass(frozen=True)
class RowView:
    y: float
    entry: Entry
    is_player: bool
    red: float = 0.0

class Shatter:
    red: float
```

Garantias novas: o foguete sempre parte de `y = 10` e sobe ≥ 1 linha; todo nome atingido termina
com `red == 1`; um `Scoreboard` novo não tem vermelho.
