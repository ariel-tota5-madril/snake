# Contract: língua (`snake.core`, `snake.tongue`, `snake.flow`)

Todos os módulos puros: sem `pygame`, `time` ou `datetime`.

## `snake.core`

```python
@dataclass(frozen=True)
class TongueShot:
    direction: Direction
    reach: int              # casas alcançadas (0..3)
    ate: bool
    target: Cell | None     # casa da fruta comida

class Game:
    def tongue(self, reach: int = 3) -> TongueShot: ...
```

Garantias: só come a fruta normal; parede e corpo bloqueiam; comer = placar +1, nova fruta e
crescimento de 1 no próximo passo; com `status != RUNNING` devolve `reach=0, ate=False`.

## `snake.tongue`

```python
COOLDOWN_MS = 8000
REACH = 3
ANIM_MS = 300

class Tongue:
    remaining_ms: float
    shot: TongueShot | None
    def fire(self, shot: TongueShot) -> None: ...
    def update_cooldown(self, dt_ms: float) -> bool: ...   # True ao ficar pronta
    def update_anim(self, dt_ms: float) -> None: ...
    @property
    def ready(self) -> bool: ...
    @property
    def progress(self) -> float: ...    # 0..1
    @property
    def extension(self) -> float: ...   # 0..1..0
```

## `snake.flow` — delta

| Membro | Contrato |
|--------|----------|
| `space()` | `PLAYING` e língua pronta e não bloqueada: dispara (`TONGUE`; se comeu, efeitos e sons de coleta e checagem do limiar do Frenzy); `PLAYING` sem poder disparar: nada; outras fases: `confirm()` |
| `tongue`, `tongue_locked`, `icon_pulse` | estado para o desenho |
| `SoundEvent.TONGUE`, `SoundEvent.TONGUE_READY` | novos |

Garantias: a recarga só anda em `PLAYING`; `TONGUE_READY` uma vez por recarga, nunca durante o
Frenzy; restart e "Tela inicial" deixam a língua pronta sem tocar som.
