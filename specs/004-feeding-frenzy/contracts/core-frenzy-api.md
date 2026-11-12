# Contract: `snake.core` (delta) e `snake.frenzy` (novo)

## `snake.core.Game` — delta sobre a 001

| Membro | Contrato |
|--------|----------|
| `specials: dict[Cell, int]` | frutas especiais → variante (0 roxa, 1 dourada) |
| `in_frenzy: bool` | `True` entre `start_frenzy()` e `end_frenzy()`/`restart()` |
| `start_frenzy(count: int = 10) -> int` | remove a fruta normal; sorteia até `count` casas livres distintas (determinístico pela seed); devolve quantas surgiram (0 se não há casa livre, e então o Frenzy não começa) |
| `end_frenzy() -> None` | limpa `specials` e sorteia nova fruta normal |
| `fail() -> None` | `status = GAME_OVER` |
| `step()` | no Frenzy: entrar numa casa especial a remove; o tamanho e o placar não mudam |
| `restart()` | também limpa `specials` |

Garantias: o comprimento da cobra é o mesmo antes de `start_frenzy()` e depois de
`end_frenzy()`; nenhuma especial nasce em cima da cobra; mesma seed + mesmas entradas → mesmas
casas especiais.

## `snake.frenzy` (puro: sem pygame, sem time)

```python
BASE_STEP_MS = 125
MIN_STEP_MS = 70
FRENZY_SPEEDUP = 1.5
FRENZY_MIN_STEP_MS = 50
FIRST_THRESHOLD = 10
FRENZY_MS = 20_000
SPECIAL_COUNT = 10
WARNING_SECONDS = 5

def step_interval_ms(length: int, frenzy: bool = False) -> float: ...
def threshold(n: int) -> int: ...          # 10, 20, 40, 80, ...

class Frenzy:
    remaining_ms: float
    def __init__(self, duration_ms: float = FRENZY_MS) -> None: ...
    def update(self, dt_ms: float) -> list[int]: ...   # segundos de aviso que começaram
    @property
    def seconds_left(self) -> int: ...      # teto, em segundos
    @property
    def warning(self) -> bool: ...          # 0 < seconds_left <= 5
    @property
    def expired(self) -> bool: ...
```

Exemplos: `step_interval_ms(3) == 125`; `step_interval_ms(13) == 115`;
`step_interval_ms(58) == 70`; `step_interval_ms(100) == 70`;
`step_interval_ms(13, frenzy=True) ≈ 76,7`; `step_interval_ms(100, frenzy=True) == 50`.

## `snake.juice` — delta

| Membro | Contrato |
|--------|----------|
| `ease_in(t)` | `t²`, com `t` limitado a [0, 1] |
| `ParticleBurst(origin, rng, count=16, speed=(2.5, 7.5), life_ms=600, tint="fruit")` | padrões iguais aos da 002; `tint` é um rótulo lido pelo desenho |
