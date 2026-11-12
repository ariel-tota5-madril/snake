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
| `SHAKE_MS` | 400 | FR-004 |
| `SHAKE_AMPLITUDE_PX` | 8 | research §6 |
| `STEP_MS` | 125 (8 passos/s) | 001 |

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
| `progress` (derivado) | `elapsed_ms / PULSE_MS`, limitado a 1; ao chegar em 1 volta a parado |
| `scale` (derivado) | `1 + 0,5·sen(π·progress)`; 1 quando parado |
| `flash` (derivado) | `1 − progress`; 0 quando parado (0 = cor original, 1 = cor do flash) |

## ScreenShake

| Campo | Regra |
|-------|-------|
| `elapsed_ms` | `None` quando parado; 0 ao disparar |
| `amplitude` (derivado) | `SHAKE_AMPLITUDE_PX · (1 − elapsed_ms / SHAKE_MS)` |
| `offset` | (dx, dy) sorteados em [−amplitude, amplitude] a cada `update`; (0, 0) quando parado |
| `done` | `elapsed_ms ≥ SHAKE_MS` |

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
          comeu  → nova ParticleBurst na cabeça + pulse.trigger()
          GAME_OVER → shake.trigger() ───────────────────────► SHAKING
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
`MENU_OUT`; Espaço/Enter em `PLAYING`. Partículas e pulso continuam atualizando em todas as fases.
