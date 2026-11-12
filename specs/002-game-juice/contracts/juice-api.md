# Contract: `snake.juice` (efeitos visuais, lógica pura)

Nenhum tipo do Pygame. Todo tempo entra por `update(dt_ms)`; toda aleatoriedade vem de um
`random.Random` injetado.

## Funções

| Função | Retorno |
|--------|---------|
| `ease_out(p: float) -> float` | `1 − (1 − p)³`, com `p` limitado a [0, 1]; `ease_out(0) == 0`, `ease_out(1) == 1` |

## `ParticleBurst(origin: tuple[float, float], rng: random.Random)`

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
| `scale` | 1 parado; > 1 durante o pulso; volta a 1 ao final |
| `flash` | 0 parado; 1 no disparo; decai até 0 |

## `ScreenShake(rng: random.Random)`

| Membro | Efeito |
|--------|--------|
| `trigger()` | começa o tremor |
| `update(dt_ms)` | avança e sorteia um novo `offset` dentro da amplitude atual |
| `offset` | `(dx, dy)` em px; exatamente `(0, 0)` quando parado ou terminado |
| `done` | `True` após 400 ms do disparo |

## Garantias

- Mesmo RNG semeado + mesma sequência de `trigger`/`update` → mesmos valores.
- Nenhuma função lê o relógio nem importa `pygame`, `time` ou `datetime`.
