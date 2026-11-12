# Contract: `snake.juice` (efeitos visuais, lógica pura)

Nenhum tipo do Pygame. Todo tempo entra por `update(dt_ms)`; toda aleatoriedade vem de um
`random.Random` injetado.

## Funções

| Função | Retorno |
|--------|---------|
| `ease_out(p: float) -> float` | `1 − (1 − p)³`, com `p` limitado a [0, 1]; `ease_out(0) == 0`, `ease_out(1) == 1` |

## `ParticleBurst(origin: tuple[float, float], rng: random.Random)`

`origin` e as posições estão em casas da grade.

| Membro | Efeito |
|--------|--------|
| `particles` | lista de partículas vivas (`x`, `y`, `life` em [0, 1]) |
| `update(dt_ms)` | move, envelhece e remove partículas mortas |
| `done` | `True` quando não há partículas vivas (no máximo 600 ms após criar) |

## `ScorePulse()`

| Membro | Efeito |
|--------|--------|
| `trigger()` | começa (ou reinicia) o pulso |
| `update(dt_ms)` | avança; ao passar de 300 ms volta a parado |
| `scale` | 1 parado; 1,8 aos 60 ms; ~0,9 aos 180 ms; 1 aos 300 ms |
| `warmth` | 0 (branco) no disparo → 1 (amarelo) aos 60 ms; 0 parado |
| `flash` | 0 parado; 1 no disparo; decai até 0 aos 300 ms |

## `ScreenShake(rng: random.Random)`

| Membro | Efeito |
|--------|--------|
| `trigger(amplitude, duration_ms)` | começa (ou substitui) um tremor; amplitude em casas |
| `update(dt_ms)` | avança e sorteia um novo `offset` dentro da amplitude atual |
| `offset` | `(dx, dy)` em casas; exatamente `(0, 0)` quando parado ou terminado |
| `done` | `True` após `duration_ms` do disparo |

Constantes: `COLLISION_SHAKE = (1/3, 400)`, `EAT_SHAKE = (1/9, 150)`.

## Garantias

- Mesmo RNG semeado + mesma sequência de `trigger`/`update` → mesmos valores.
- Nenhuma função lê o relógio nem importa `pygame`, `time` ou `datetime`.
