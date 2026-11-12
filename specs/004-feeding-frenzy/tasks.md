---

description: "Task list for 004-feeding-frenzy"
---

# Tasks: Feeding Frenzy — velocidade progressiva e modo de sobrevivência

**Input**: Design documents from `/specs/004-feeding-frenzy/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/core-frenzy-api.md, contracts/flow-api.md, quickstart.md

**Tests**: INCLUÍDOS. A constituição (Princípio II) exige test-first: cada teste DEVE ser escrito
e falhar antes da implementação correspondente. Os testes das features 001–003 DEVEM continuar
passando; os que assumem passo fixo de 125 ms depois de a cobra crescer DEVEM ser ajustados,
porque o FR-002 mudou a velocidade.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Paths seguem o layout `src/` + `tests/` do plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: módulo novo e a guarda de pureza

- [X] T001 [P] Create `src/snake/frenzy.py` with the module docstring and the constants of data-model.md (`BASE_STEP_MS`, `MIN_STEP_MS`, `START_LENGTH`, `FRENZY_SPEEDUP`, `FRENZY_MIN_STEP_MS`, `FIRST_THRESHOLD`, `FRENZY_MS`, `SPECIAL_COUNT`, `WARNING_SECONDS`)
- [X] T002 [P] Extend `tests/test_core_purity.py` to assert `snake.frenzy` imports no `pygame`, `time` or `datetime`

**Checkpoint**: `pytest` verde; o jogo continua igual ao da 003.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: efeitos parametrizáveis usados pelas partículas coloridas (US2) e pelos detritos (US3)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Write failing tests in `tests/test_juice.py`: `ease_in(t) == t²` clamped to [0, 1]; `ParticleBurst(origin, rng, count=12, speed=(6, 14), life_ms=900, tint="purple")` creates 12 particles with speeds in range, is done after 900 ms and exposes `tint`; defaults remain 16 particles, 2.5–7.5 cells/s, 600 ms, `tint == "fruit"`
- [X] T004 Implement `ease_in` and the `count`/`speed`/`life_ms`/`tint` parameters of `ParticleBurst` in `src/snake/juice.py`

**Checkpoint**: `pytest` verde; o jogo continua igual.

---

## Phase 3: User Story 1 - Cobra mais rápida conforme cresce (Priority: P1) 🎯 MVP

**Goal**: o intervalo entre passos segue `max(70, 125 − (tamanho − 3))` ms (FR-001 a FR-003).

**Independent Test**: comer várias frutas e perceber a aceleração; reiniciar e voltar à velocidade inicial (quickstart.md itens 1 e 10).

### Tests for User Story 1 ⚠️

- [X] T005 [P] [US1] Write failing tests in `tests/test_speed.py`: `step_interval_ms(3) == 125`, `(4) == 124`, `(13) == 115`, `(58) == 70`, `(100) == 70`; monotonically non-increasing in length
- [X] T006 [P] [US1] Write failing tests in `tests/test_flow.py`: after the snake grows to length 4, the next step happens after 124 ms (not before); several steps in one `update` use the interval recalculated after each step; after Restart the interval is 125 ms again

### Implementation for User Story 1

- [X] T007 [US1] Implement `step_interval_ms(length, frenzy=False)` (normal curve only) in `src/snake/frenzy.py`
- [X] T008 [US1] Replace the fixed `STEP_MS` in `Flow._update_playing` with the interval from `step_interval_ms(len(game.snake))`, recalculated after each step, in `src/snake/flow.py`
- [X] T009 [US1] Adjust existing timing-dependent tests in `tests/test_flow.py` (and helpers) that assume 125 ms per step after the snake has grown

**Checkpoint**: a cobra acelera ao crescer; `pytest` verde; jogável.

---

## Phase 4: User Story 2 - Modo Feeding Frenzy (Priority: P1)

**Goal**: regras completas do modo: limiares 10/20/40/…, frutas especiais roxas/douradas, cobra 1,5× mais rápida sem crescer nem pontuar, cronômetro de 20 s com aviso nos últimos 5 s, sucesso volta ao normal, tempo esgotado com alarme e fim de jogo (FR-004 a FR-012, FR-016, FR-018, FR-019). Sem a abertura (US3), o modo começa direto; sem "SURVIVED!" (US4), o sucesso volta direto ao jogo normal.

**Independent Test**: chegar a 10 pontos, comer as 10 especiais a tempo; repetir deixando o tempo acabar (quickstart.md itens 3–6, 8–11).

### Tests for User Story 2 ⚠️

- [X] T010 [P] [US2] Write failing tests in `tests/test_speed.py`: `step_interval_ms(13, frenzy=True) ≈ 76.67`; `step_interval_ms(100, frenzy=True) == 50`; Frenzy interval is never above the normal one for the same length
- [X] T011 [P] [US2] Write failing tests in `tests/test_frenzy.py` for `threshold(n)` (10, 20, 40, 80, 160) and `Frenzy`: starts at 20 000 ms / `seconds_left == 20`; `update` never goes below 0; `seconds_left` is the ceiling; `warning` only for 1–5 s; `expired` only at 0; `update` returns the warning seconds that just started, in order, including several in one big `dt`
- [X] T012 [P] [US2] Write failing tests in `tests/test_frenzy.py` for the core: `start_frenzy()` removes the normal food, creates 10 specials on free distinct cells with alternating variants 0/1, returns 10, is reproducible with the same seed, and creates fewer when free cells are scarce (0 → returns 0); in Frenzy, entering a special removes it with no growth and no score; `end_frenzy()` clears specials, respawns normal food and the length equals the length before `start_frenzy()`; `fail()` sets `GAME_OVER`; `restart()` clears specials
- [X] T013 [P] [US2] Write failing tests in `tests/test_sounds.py`: `SFX` has `TIMER_TICK` and `TIMEOUT_ALARM`, `MUSIC` has `MUSIC_FRENZY`; the Frenzy song lasts a whole number of bars at 180 BPM and starts/ends near zero
- [X] T014 [US2] Write failing tests in `tests/test_flow.py`: Frenzy starts exactly when the score reaches 10, then 20 and 40 (not at 11, 15, 30); on start: `MUSIC_STOP` then `MUSIC_FRENZY`, specials on the board, `frenzy.seconds_left == 20`; steps use the Frenzy interval; eating a special emits `EAT` (no `PULSE_POP`), adds a burst with the fruit's tint, keeps score and length; timer runs only in `PLAYING` (unchanged across pause and resume); `TIMER_TICK` at 5, 4, 3, 2, 1 with `timer_pulse` triggered; last special → back to normal with `MUSIC_GAME`, normal food and the same length; last special in the same frame the timer expires → success; timer expiring with specials left → `TIMEOUT` (`MUSIC_STOP`, `TIMEOUT_ALARM`, no `CRASH`, no shake, `game.status == GAME_OVER`, `timeout_blink` toggles), then after 1 200 ms `MENU_IN` with `LOSE`; collision during Frenzy → normal `SHAKING`; inputs ignored in `TIMEOUT`; Restart and "Tela inicial" reset `frenzy` and `frenzy_count`

### Implementation for User Story 2

- [X] T015 [US2] Implement the Frenzy speed bonus, `threshold(n)` and the `Frenzy` timer in `src/snake/frenzy.py`
- [X] T016 [US2] Implement `specials`, `in_frenzy`, `start_frenzy()`, `end_frenzy()`, `fail()`, the special-eating rule in `step()` and the cleanup in `restart()` in `src/snake/core.py`
- [X] T017 [US2] Add `TIMER_TICK`, `TIMEOUT_ALARM` and `MUSIC_FRENZY` to `SoundEvent` in `src/snake/flow.py` and synthesize the tick, the alarm and the 180 BPM Frenzy song (research.md §9) in `src/snake/sounds.py`
- [X] T018 [US2] Implement in `src/snake/flow.py`: `frenzy`, `frenzy_count`, `timer_pulse`, the threshold check after eating, Frenzy steps and timer in `_update_playing` (steps first, then success/timeout), the `TIMEOUT` phase, `timer_visible`, `timeout_blink`, and the reset on Restart / "Tela inicial"
- [X] T019 [US2] Draw in `src/snake/app.py`: specials as purple/gold squares with a pulsing halo; tinted particles (`fruit`/`purple`/`gold`); the big timer at the top center with "N restantes" below while the score is hidden; red + pulse in the warning seconds; red blinking "0" in `TIMEOUT`

**Checkpoint**: Frenzy jogável de ponta a ponta (sem abertura e sem "SURVIVED!"); `pytest` verde.

---

## Phase 5: User Story 3 - Abertura "FEEDING FRENZY" com impacto (Priority: P2)

**Goal**: partida e música param; "FEEDING" (roxo) e "FRENZY" (amarelo) carimbadas na diagonal com boom, detritos e tremor; música do Frenzy só depois (FR-013 a FR-015).

**Independent Test**: chegar a 10 pontos e observar a sequência completa (quickstart.md item 2).

### Tests for User Story 3 ⚠️

- [X] T020 [P] [US3] Write failing tests in `tests/test_sounds.py`: `SFX` has `BOOM` (~600 ms, starts/ends near zero, louder than `EAT`'s relative volume)
- [X] T021 [US3] Write failing tests in `tests/test_flow.py`: reaching the threshold goes to `FRENZY_INTRO` (`MUSIC_STOP`, specials already on the board, timer not running, snake does not move); `stamp_scales` is `(None, None)` before 200 ms, FEEDING 4.0 → 1.0 between 200 and 500 ms, FRENZY between 800 and 1 100 ms; `BOOM` exactly at 500 ms and 1 100 ms, each adding 5 bursts (tints `purple`, then `gold`) and a shake; `stamp_alpha` falls from 1 to 0 between 1 600 and 1 900 ms; Esc, arrows and Enter ignored; at 1 900 ms → `PLAYING` with `MUSIC_FRENZY` and the timer at 20 s

### Implementation for User Story 3

- [X] T022 [P] [US3] Add `BOOM` to `SoundEvent` in `src/snake/flow.py` and synthesize it in `src/snake/sounds.py` (noise with falling clock + triangle sweep, 600 ms, relative volume 1.0)
- [X] T023 [US3] Implement the `FRENZY_INTRO` phase in `src/snake/flow.py` (timeline of research.md §6, `stamp_scales`, `stamp_alpha`, `stamp_origins`, debris bursts and `STAMP_SHAKE`), replacing the direct start of US2
- [X] T024 [US3] Draw the stamps in `src/snake/app.py`: words rendered once in a big font with a dark outline, rotated ~15°, scaled per frame by `stamp_scales` and faded by `stamp_alpha`; purple/gold colors

**Checkpoint**: abertura completa com impacto; `pytest` verde.

---

## Phase 6: User Story 4 - "SURVIVED!" ao superar o modo (Priority: P3)

**Goal**: ao comer a última especial a tempo, a partida pausa e "SURVIVED!" azul entra suave e sai; depois a partida retoma com a música normal (FR-017).

**Independent Test**: superar um Frenzy e observar a pausa, a palavra e a retomada (quickstart.md item 7).

### Tests for User Story 4 ⚠️

- [X] T025 [US4] Write failing tests in `tests/test_flow.py`: eating the last special goes to `SURVIVED` (`MUSIC_STOP`, normal food back, same length, timer hidden, snake stopped); `survived_progress` rises 0 → 1 until 500 ms, stays 1 until 1 000 ms and falls to 0 at 1 500 ms; inputs ignored; at 1 500 ms → `PLAYING` with `MUSIC_GAME` and the normal speed for the length

### Implementation for User Story 4

- [X] T026 [US4] Implement the `SURVIVED` phase and `survived_progress` in `src/snake/flow.py`, replacing the direct return to normal of US2
- [X] T027 [US4] Draw "SURVIVED!" in light blue in `src/snake/app.py` (alpha, scale 0.85 → 1 and a small rise from `survived_progress`)

**Checkpoint**: todas as histórias funcionando; `pytest` verde.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: documentação, desempenho e validação final

- [X] T028 [P] Update `README.md` with the progressive speed and the Feeding Frenzy rules
- [X] T029 Measure frame time during the intro and an active Frenzy with the headless drive (SC-006: p95 under 16.7 ms at 1440×1440) and optimize drawing if needed
- [X] T030 Run the quickstart.md validation (manual, by the user)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup — bloqueia as histórias
- **US1 (Phase 3)**: depende do Foundational
- **US2 (Phase 4)**: depende de US1 (a velocidade do Frenzy é um bônus sobre a curva normal e os testes de passo já usam o intervalo variável)
- **US3 (Phase 5)**: depende de US2 (substitui o início direto do modo)
- **US4 (Phase 6)**: depende de US2 (substitui a volta direta ao normal); independente de US3
- **Polish (Phase 7)**: depois das histórias desejadas

### Within Each User Story

- Testes escritos e falhando antes da implementação
- `frenzy.py` e `core.py` antes do `flow.py`; `flow.py` antes do `app.py`
- Catálogo de sons junto com o enum de eventos

### Parallel Opportunities

- T001 e T002
- T005 e T006
- T010, T011, T012 e T013 (arquivos diferentes)
- T020 com T021 (arquivos diferentes); T022 com T023 não (ambos tocam `flow.py`)
- US3 e US4 podem ser feitas em paralelo depois de US2, com cuidado no `flow.py`

---

## Parallel Example: User Story 2

```bash
# Testes de regra pura, em arquivos diferentes:
Task: "T010 Frenzy speed tests in tests/test_speed.py"
Task: "T011 threshold and Frenzy timer tests in tests/test_frenzy.py"
Task: "T013 new sounds tests in tests/test_sounds.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup + Foundational
2. US1: velocidade progressiva
3. **STOP and VALIDATE**: jogar e sentir a aceleração

### Incremental Delivery

1. US1 → cobra acelera (já é uma melhoria jogável)
2. US2 → Frenzy completo nas regras, com cronômetro e sons de tempo
3. US3 → abertura com carimbos e boom
4. US4 → "SURVIVED!"
5. Polish → README, desempenho, validação manual

---

## Notes

- [P] tasks = arquivos diferentes, sem dependências
- Cada história termina com o jogo abrindo e `pytest` verde (Princípio V)
- Commit ao fim de cada fase
