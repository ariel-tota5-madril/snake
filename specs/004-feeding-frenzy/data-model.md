# Data Model: Feeding Frenzy

## Game (`core.py`) — campos novos

| Campo | Tipo | Regra |
|-------|------|-------|
| `specials` | `dict[Cell, int]` | frutas especiais ativas → variante (0 roxa, 1 dourada); vazio fora do Frenzy |
| `in_frenzy` | `bool` (propriedade) | `True` entre `start_frenzy()` e `end_frenzy()`/`restart()` |

### Ordem do `step()` (delta sobre a 001)

1. Aplica direção pendente; calcula a nova cabeça.
2. Fora do tabuleiro → `GAME_OVER`.
3. `eating = head == food` (no Frenzy, `food` é `None`, então nunca come fruta normal).
4. Corpo considerado: sem a cauda (a não ser que esteja comendo fruta normal). Bateu → `GAME_OVER`.
5. Move a cabeça; se não comeu fruta normal, a cauda anda.
6. **Novo**: se a cabeça está numa fruta especial, ela é removida de `specials` (sem crescer, sem
   pontuar).
7. Comeu fruta normal: `score += 1`, nova fruta; sem casa livre → `WON`.

### Operações novas

| Operação | Efeito |
|----------|--------|
| `start_frenzy(count=10) -> int` | `food = None`; sorteia `min(count, livres)` casas (`rng.sample` sobre a lista ordenada de casas livres); variante = índice do sorteio % 2; devolve quantas surgiram |
| `end_frenzy()` | limpa `specials`; sorteia nova fruta normal |
| `fail()` | `status = GAME_OVER` (tempo esgotado) |
| `restart()` | também limpa `specials` |

## `frenzy.py` (novo)

| Nome | Definição |
|------|-----------|
| `BASE_STEP_MS = 125`, `MIN_STEP_MS = 70`, `START_LENGTH = 3` | curva normal |
| `FRENZY_SPEEDUP = 1.5`, `FRENZY_MIN_STEP_MS = 50` | bônus do Frenzy |
| `FIRST_THRESHOLD = 10` | primeiro limiar |
| `FRENZY_MS = 20000`, `SPECIAL_COUNT = 10`, `WARNING_SECONDS = 5` | regras do modo |
| `step_interval_ms(length, frenzy=False) -> float` | normal `max(70, 125 − (length − 3))`; Frenzy `max(50, normal / 1.5)` |
| `threshold(n) -> int` | `10 × 2ⁿ` |
| `Frenzy` | cronômetro do modo (abaixo) |

### `Frenzy`

| Campo / método | Regra |
|----------------|-------|
| `remaining_ms: float` | começa em `FRENZY_MS`; nunca negativo |
| `update(dt_ms) -> list[int]` | desconta `dt`; devolve os segundos de aviso (5…1) que começaram neste update, em ordem |
| `seconds_left: int` | `ceil(remaining_ms / 1000)` |
| `warning: bool` | `0 < seconds_left <= 5` |
| `expired: bool` | `remaining_ms == 0` |

## Flow — estado novo

| Campo | Tipo | Regra |
|-------|------|-------|
| `frenzy` | `Frenzy \| None` | ativo do início da abertura até o fim de `SURVIVED`/`TIMEOUT` |
| `frenzy_count` | `int` | Frenzies já iniciados na partida; zera em restart e "Tela inicial" |
| `specials_total` | `int` | quantas especiais surgiram (para o desenho, se útil) |
| `timer_pulse` | `ScorePulse` | pulso do cronômetro nos últimos 5 s |

### Fases novas e transições

```text
PLAYING ──(comeu fruta normal e score == threshold(frenzy_count), e há casa livre)──▶ FRENZY_INTRO
FRENZY_INTRO ──(1 900 ms)──▶ PLAYING (com frenzy ativo)
PLAYING [frenzy] ──(specials vazio após os passos do quadro)──▶ SURVIVED
PLAYING [frenzy] ──(cronômetro expirou e ainda há specials)──▶ TIMEOUT
PLAYING [frenzy] ──(colisão)──▶ SHAKING (como hoje; frenzy é descartado)
SURVIVED ──(1 500 ms)──▶ PLAYING (normal)
TIMEOUT ──(1 200 ms)──▶ MENU_IN (LOSE)
PLAYING [frenzy] ──(Esc)──▶ PAUSE_IN … RESUME ──▶ PLAYING [frenzy] (cronômetro parado o tempo todo)
```

Esc, setas e Enter são ignorados em `FRENZY_INTRO`, `SURVIVED` e `TIMEOUT`. Efeitos (partículas,
tremor, pulsos) continuam animando nessas fases.

### Eventos sonoros novos

| Momento | Evento(s) |
|---------|-----------|
| entra em `FRENZY_INTRO` | `MUSIC_STOP` |
| impacto de cada palavra (500 ms e 1 100 ms) | `BOOM` |
| fim da abertura | `MUSIC_FRENZY` |
| come fruta especial | `EAT` (sem `PULSE_POP`) |
| começa cada um dos segundos 5, 4, 3, 2, 1 | `TIMER_TICK` |
| entra em `SURVIVED` | `MUSIC_STOP` |
| fim de `SURVIVED` | `MUSIC_GAME` |
| entra em `TIMEOUT` | `MUSIC_STOP`, `TIMEOUT_ALARM` |
| fim de `TIMEOUT` | `LOSE` (via menu de fim, como hoje) |
