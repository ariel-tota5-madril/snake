# Data Model: Áudio, pausa e Opções

## Constantes

| Nome | Valor | Origem |
|------|-------|--------|
| `SAMPLE_RATE` | 22 050 Hz, mono, 16 bits | research §7 |
| `RAMP_MS` | 2 | research §3 |
| `PULSE_POP_DELAY_MS` | 60 | FR-004 (pico do pulso da 002) |
| `RESUME_MS` / `RESUME_STEP_MS` | 1500 / 500 | Clarificação 2 |
| `MUSIC_GAIN` | 0,5 | FR-011 |
| `PAUSE_DUCK` | 0,35 | FR-015 |
| `VOLUME_STEP` | 10 | FR-017 |
| `DEFAULT_VOLUMES` | música 60, efeitos 80 | Assumptions |

## Voice / Note (synth)

| Campo | Regra |
|-------|-------|
| `wave` | `square50`, `square25`, `square12`, `triangle`, `noise` |
| `freq` | Hz no início da nota (0 = pausa) |
| `freq_end` | Hz no fim (opcional; desliza linearmente) |
| `ms` | duração |
| `volume` | 0–1 antes do envelope |

Saída: `array('h')` com amostras em [−32767, 32767]; primeira e última amostra de cada nota
≈ 0 (rampa de `RAMP_MS`).

## SoundEvent (enum, emitido pelo Flow)

`STEP`, `EAT`, `PULSE_POP`, `CRASH`, `COUNT`, `GO`, `NAV`, `CONFIRM`, `LOSE`, `WIN`,
`VOLUME_PREVIEW`, `MUSIC_TITLE`, `MUSIC_GAME`, `MUSIC_STOP`, `MUSIC_DUCK`, `MUSIC_UNDUCK`.

| Evento | Quando o Flow emite |
|--------|---------------------|
| `STEP` | a cada `game.step()` que deixa a partida rodando |
| `EAT` | passo em que a pontuação aumenta (junto com as partículas) |
| `PULSE_POP` | 60 ms de jogo após `EAT` (agendado; congela na pausa) |
| `CRASH` | passo que termina em `GAME_OVER` (junto com o tremor) |
| `COUNT` | entrada em `COUNTDOWN` e a cada número seguinte; idem em `RESUME` |
| `GO` | fim de `COUNTDOWN` ou `RESUME` (cobra volta a andar) |
| `NAV` | `move_up`/`move_down` em qualquer menu que mudou a seleção; ←/→ em Opções que mudou o valor |
| `CONFIRM` | confirmação aceita em tela inicial, pausa, fim ou Opções ("Voltar") |
| `LOSE` / `WIN` | abertura do menu de fim após colisão / vitória |
| `VOLUME_PREVIEW` | ←/→ no slider "Efeitos" que mudou o valor |
| `MUSIC_TITLE` | entrada em `TITLE_IN` |
| `MUSIC_GAME` | início de `PLAYING` vindo de `COUNTDOWN` |
| `MUSIC_STOP` | fim da partida (antes de `LOSE`/`WIN`) e saída da pausa para a tela inicial |
| `MUSIC_DUCK` / `MUSIC_UNDUCK` | entrada em `PAUSE_IN` / saída da pausa para `RESUME` |

Mudança de direção e teclas ignoradas não emitem nada (FR-010).

## AudioSettings

| Campo | Regra |
|-------|-------|
| `music`, `sfx` | inteiros 0–100, múltiplos de 10 |
| `adjust(field, ±1)` | soma ±10, limitado a [0, 100]; retorna se mudou |
| `load(path)` | lê JSON; em qualquer erro ou valor inválido usa `DEFAULT_VOLUMES` |
| `save(path)` | grava JSON, criando a pasta se preciso |

## Menu (generalizado)

`Menu(options)`: `selected`, `move_up() -> bool`, `move_down() -> bool`, `confirm()`; sem volta
circular. Opções: `TITLE_OPTIONS = (PLAY, OPTIONS)`, `PAUSE_OPTIONS = (CONTINUE, OPTIONS, TITLE)`,
`END_OPTIONS = (RESTART, OPTIONS, QUIT)`, `SETTINGS_OPTIONS = (MUSIC, SFX, BACK)`.

## Fases novas e transições (delta sobre a 002)

```text
TITLE ──confirm PLAY─────────────────────────────────► TITLE_OUT (→ COUNTDOWN, como antes)
TITLE / PAUSE / MENU ──confirm OPTIONS──────────────► OPTIONS_IN ─300 ms─► OPTIONS
OPTIONS ──←/→ em MUSIC ou SFX → settings.adjust
OPTIONS ──confirm BACK ou escape()──────────────────► OPTIONS_OUT ─300 ms─► fase de origem
          (salva os volumes ao sair)
PLAYING ──escape()──────────────────────────────────► PAUSE_IN ─300 ms─► PAUSE
PAUSE ──confirm CONTINUE ou escape()────────────────► PAUSE_OUT ─300 ms─► RESUME
RESUME ──1500 ms────────────────────────────────────► PLAYING (sem passo imediato)
PAUSE ──confirm TITLE───────────────────────────────► PAUSE_OUT ─300 ms─► TITLE_IN (partida reiniciada)
MENU ──confirm RESTART / QUIT───────────────────────► como na 002
```

Em `PAUSE_*`, `RESUME`, `OPTIONS*` vindos da pausa, o tempo do jogo e dos efeitos (passos,
partículas, pulso, tremor, `PULSE_POP` agendado) não avança. `escape()` fora de `PLAYING`,
`PAUSE` e `OPTIONS` é ignorado.
