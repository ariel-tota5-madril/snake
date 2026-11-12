# Data Model: Game juice

Tempos em milissegundos. Posições das partículas em **casas da grade** (o adaptador converte
para pixels); origem = casa da cabeça. Offsets do tremor em pixels.

## Constantes

| Nome | Valor | Origem |
|------|-------|--------|
| `UI_ANIM_MS` | 300 | FR-007, FR-008 (≤ 400) |
| `COUNTDOWN_MS` | 3000 (3 números × 1000) | FR-012 |
| `PARTICLE_LIFE_MS` | 600 | FR-001 |
| `PARTICLES_PER_BURST` | 16 | research §4 |
| `PULSE_MS` | 300 | FR-002 |
| `PULSE_PEAK_MS` / `PULSE_PEAK` | 60 / 1,8 | FR-002 |
| `PULSE_DIP_MS` / `PULSE_DIP` | 180 / 0,9 | FR-002 |
| `COLLISION_SHAKE` | 1/3 de casa, 400 ms | FR-004 |
| `EAT_SHAKE` | 1/9 de casa, 150 ms | FR-015 |
| `STEP_MS` | 125 (8 passos/s) | 001 |
| `GRID` | 30 × 30 casas | FR-014 |

## Particle

| Campo | Regra |
|-------|-------|
| `x`, `y` | posição atual em casas, começa na casa da cabeça (o adaptador desenha no centro da casa) |
| `vx`, `vy` | velocidade em casas/s (2,5 a 7,5), de ângulo e módulo sorteados no RNG dos efeitos |
| `age_ms` | começa em 0; partícula morre quando `age_ms ≥ PARTICLE_LIFE_MS` |
| `life` (derivado) | `1 − age_ms / PARTICLE_LIFE_MS`, usado para alfa e tamanho |

## ParticleBurst

- Conjunto de `PARTICLES_PER_BURST` partículas criadas no mesmo instante.
- `update(dt)`: move e envelhece todas; `done` quando todas morreram.

## ScorePulse

| Campo | Regra |
|-------|-------|
| `elapsed_ms` | `None` quando parado; 0 ao disparar (reinicia se já ativo) |
| `scale` (derivado) | 1,0→1,8 até 60 ms; 1,8→0,9 até 180 ms; 0,9→1,0 até 300 ms; 1 quando parado |
| `warmth` (derivado) | 0 (branco) → 1 (amarelo) nos primeiros 60 ms; 1 depois; 0 quando parado |
| `flash` (derivado) | `1 − elapsed_ms / PULSE_MS`; 0 quando parado (força do flash sobre a cor normal) |

## ScreenShake

| Campo | Regra |
|-------|-------|
| `elapsed_ms`, `duration_ms`, `peak` | definidos em `trigger(amplitude, duration_ms)`; um novo `trigger` substitui o atual |
| `amplitude` (derivado) | `peak · (1 − elapsed_ms / duration_ms)`, em casas |
| `offset` | (dx, dy) em casas, sorteados em [−amplitude, amplitude] a cada `update`; (0, 0) quando parado |
| `done` | `elapsed_ms ≥ duration_ms` |

## Phase (enum) e Flow

| Campo do Flow | Regra |
|---------------|-------|
| `phase` | fase atual (ver transições) |
| `phase_ms` | tempo decorrido na fase atual; zera a cada transição |
| `game` | `Game` da 001, criado com o RNG do jogo |
| `menu` | `EndMenu` da 001 enquanto em `MENU_IN`/`MENU`/`MENU_OUT`; senão `None` |
| `bursts` | lista de `ParticleBurst` ativas (removidas quando `done`) |
| `pulse` | `ScorePulse` do placar |
| `shake` | `ScreenShake` da tela |
| `quit_requested` | `True` depois de "Quit" ou de fechar a janela |
| `countdown_number` (derivado) | em `COUNTDOWN`: 3, 2 ou 1 conforme `phase_ms` |
| `ui_progress` (derivado) | em fases `_IN`/`_OUT`: `ease_out(phase_ms / UI_ANIM_MS)` |

## Transições de fase

```text
TITLE_IN ──phase_ms ≥ UI_ANIM_MS──────────────────────────────► TITLE
TITLE ──confirm (Espaço/Enter)────────────────────────────────► TITLE_OUT
TITLE_OUT ──phase_ms ≥ UI_ANIM_MS─────────────────────────────► COUNTDOWN
COUNTDOWN ──phase_ms ≥ COUNTDOWN_MS───────────────────────────► PLAYING
PLAYING ──a cada STEP_MS: game.step()
          comeu  → nova ParticleBurst na cabeça + pulse.trigger() + shake.trigger(EAT_SHAKE)
          GAME_OVER → shake.trigger(COLLISION_SHAKE) ────────► SHAKING
          WON ───────────────────────────────────────────────► MENU_IN (sem tremor)
SHAKING ──shake.done──────────────────────────────────────────► MENU_IN
MENU_IN ──phase_ms ≥ UI_ANIM_MS, ou qualquer tecla do menu────► MENU (a tecla é aplicada)
MENU ──↑/↓ → menu.move_up()/move_down()
       confirm: RESTART ──────────────────────────────────────► MENU_OUT
                QUIT ─────────────────────────────────────────► quit_requested
MENU_OUT ──phase_ms ≥ UI_ANIM_MS → game.restart()─────────────► COUNTDOWN
qualquer fase ──quit (fechar janela)──────────────────────────► quit_requested
```

Entradas ignoradas: setas, Espaço e Enter em `TITLE_IN`, `TITLE_OUT`, `COUNTDOWN`, `SHAKING` e
`MENU_OUT`; Espaço/Enter em `PLAYING`. Partículas, pulso e tremor continuam atualizando em todas
as fases.
