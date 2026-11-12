---

description: "Task list for 002-game-juice"
---

# Tasks: Game juice — feedback visual do Snake

**Input**: Design documents from `/specs/002-game-juice/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/juice-api.md, contracts/flow-api.md, quickstart.md

**Tests**: INCLUÍDOS. A constituição (Princípio II) exige test-first: cada teste DEVE ser escrito
e falhar antes da implementação correspondente. Os testes da 001 DEVEM continuar passando.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths seguem o layout `src/` + `tests/` do plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Módulos novos e a guarda de pureza

- [X] T001 [P] Create `src/snake/juice.py` and `src/snake/flow.py` with module docstrings only
- [X] T002 [P] Extend `tests/test_core_purity.py` to assert `snake.juice` and `snake.flow` import no `pygame`, `time` or `datetime`

**Checkpoint**: `pytest` verde; o jogo continua igual ao da 001.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o `Flow` assume o relógio de passos e o menu que hoje vivem no `app.py`, sem mudar
o comportamento da 001. Todas as histórias dependem dele.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Write failing tests in `tests/test_flow.py`: in `PLAYING`, `update(dt)` calls `game.step()` once per `STEP_MS = 125` accumulated (nothing before 125 ms); `direction(d)` turns the snake; `confirm()` is ignored while playing (FR-016 da 001)
- [X] T004 Write failing tests in `tests/test_flow.py`: on `GAME_OVER` or `WON` the flow enters `MENU` with an `EndMenu`; ↑/↓ via `direction()` move the selection; confirm `RESTART` restarts the game and returns to `PLAYING`; confirm `QUIT` and `quit()` (any phase) set `quit_requested`
- [X] T005 Write failing test in `tests/test_flow.py`: `Flow(seed=s)` produces the same food sequence as a bare `Game(seed=s)` given the same commands (SC-005)
- [X] T006 Implement `Phase` enum (all phases from data-model.md), constants (`STEP_MS`, `UI_ANIM_MS`, `COUNTDOWN_MS`, `PULSE_MS`, `SHAKE_MS`, `PARTICLE_LIFE_MS`) and `Flow(seed, width, height)` in `src/snake/flow.py`, temporarily starting in `PLAYING`, with `direction`, `confirm`, `quit`, `update` covering `PLAYING` and `MENU`, until T003–T005 pass
- [X] T007 Rewrite `src/snake/app.py` to drive a `Flow`: arrows → `direction()`, Espaço/Enter → `confirm()`, window close → `quit()`, clock `dt` → `update()`, draw board/score/menu from the flow; close when `quit_requested`

**Checkpoint**: `pytest` verde (001 + novos) e o jogo se comporta exatamente como na 001.

---

## Phase 3: User Story 1 - Recompensa visual ao comer (Priority: P1) 🎯 MVP

**Goal**: partículas na cabeça e pulso com flash no placar ao comer (FR-001, FR-002, FR-003).

**Independent Test**: comer frutas e ver partículas e o placar pulsando (quickstart.md itens 5 e 6).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Test in `tests/test_juice.py`: `ease_out(0) == 0`, `ease_out(1) == 1`, increasing in between, clamped outside [0, 1]
- [X] T009 [P] [US1] Test in `tests/test_juice.py`: `ParticleBurst` creates 16 particles at the origin; after 600 ms ("PARTICLE_LIFE_MS = 600") `done` is True and no particle remains; two bursts with equally seeded RNGs produce identical particles
- [X] T010 [P] [US1] Test in `tests/test_juice.py`: `ScorePulse` has `scale == 1` and `flash == 0` when idle; mid-pulse `scale > 1` and `0 < flash < 1`; after 300 ms ("PULSE_MS = 300") back to `scale == 1`, `flash == 0`; `trigger()` mid-pulse restarts it
- [X] T011 [US1] Test in `tests/test_flow.py`: eating adds one burst centered on the new head cell and triggers the pulse; moving without eating adds no burst; effects keep updating in every phase

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement `ease_out`, `ParticleBurst` (16 particles, speed 60–180 px/s, life 600 ms) and `ScorePulse` (300 ms, `scale = 1 + 0.5·sin(π·p)`, `flash = 1 − p`) in `src/snake/juice.py`
- [X] T013 [US1] In `src/snake/flow.py`: create the effects RNG from the seed (separate from the game RNG), detect eating by score increase after each step, spawn a burst + trigger the pulse, update and prune bursts every frame
- [X] T014 [US1] In `src/snake/app.py`: draw particles (size/alpha by `life`) and the score with `pulse.scale` and color blended toward the flash color by `pulse.flash`

**Checkpoint**: `pytest` verde; comer mostra partículas e o placar pulsa.

---

## Phase 4: User Story 2 - Impacto ao colidir (Priority: P2)

**Goal**: tremor de tela na colisão, antes do menu; sem tremor na vitória (FR-004, FR-005, FR-006).

**Independent Test**: bater na parede e ver a tela tremer antes do menu (quickstart.md item 7).

### Tests for User Story 2 ⚠️

- [X] T015 [P] [US2] Test in `tests/test_juice.py`: `ScreenShake` offset stays within the decaying amplitude (8 px → 0); after 400 ms ("SHAKE_MS = 400") `done` is True and `offset == (0, 0)`; idle offset is `(0, 0)`; deterministic with equally seeded RNGs
- [X] T016 [US2] Test in `tests/test_flow.py`: `GAME_OVER` enters `SHAKING` (no menu yet) and only after the shake is done reaches the menu; `WON` reaches the menu without shaking; inputs are ignored during `SHAKING`

### Implementation for User Story 2

- [X] T017 [P] [US2] Implement `ScreenShake` in `src/snake/juice.py`
- [X] T018 [US2] Add the `SHAKING` phase to `src/snake/flow.py` (trigger on `GAME_OVER`, go to menu when `shake.done`)
- [X] T019 [US2] In `src/snake/app.py`: offset the board drawing by `flow.shake.offset`

**Checkpoint**: `pytest` verde; colidir treme a tela e só então abre o menu.

---

## Phase 5: User Story 3 - Entrada e saída da interface (Priority: P3)

**Goal**: tela inicial, contagem regressiva com placar entrando e janela de fim com entrada/saída
animadas (FR-007, FR-008, FR-009, FR-012, FR-013).

**Independent Test**: abrir o jogo, começar, perder, reiniciar (quickstart.md itens 1–4, 8, 9).

### Tests for User Story 3 ⚠️

- [X] T020 [P] [US3] Test in `tests/test_flow.py`: a new flow starts in `TITLE_IN`, reaches `TITLE` after 300 ms ("UI_ANIM_MS = 300"); arrows and confirm are ignored in `TITLE_IN`; confirm in `TITLE` goes to `TITLE_OUT` and, 300 ms later, to `COUNTDOWN`; arrows in `TITLE` are ignored
- [X] T021 [P] [US3] Test in `tests/test_flow.py`: in `COUNTDOWN`, `countdown_number` is 3, 2, 1 for each second of "COUNTDOWN_MS = 3000"; the snake does not move and inputs are ignored; after 3000 ms the phase is `PLAYING`
- [X] T022 [P] [US3] Test in `tests/test_flow.py`: end of game → `MENU_IN` → `MENU` after 300 ms; a menu key during `MENU_IN` completes the entrance and is applied; confirm `RESTART` → `MENU_OUT` → after 300 ms the game is restarted and the phase is `COUNTDOWN` (not `TITLE`); confirm `QUIT` sets `quit_requested` immediately
- [X] T023 [P] [US3] Test in `tests/test_flow.py`: `ui_progress` goes 0→1 with easing in `_IN` phases, 1→0 in `_OUT` phases, and is 1 in `TITLE` and `MENU`

### Implementation for User Story 3

- [X] T024 [US3] In `src/snake/flow.py`: start in `TITLE_IN`; add `TITLE`, `TITLE_OUT`, `COUNTDOWN`, `MENU_IN`, `MENU_OUT` with the transitions and ignored inputs of data-model.md; expose `countdown_number` and `ui_progress`
- [X] T025 [US3] In `src/snake/app.py`: draw the title screen over the dimmed board, the countdown numbers, the score sliding in during the countdown, and scale/alpha of title and end menu by `ui_progress`

**Checkpoint**: todas as histórias funcionando; `pytest` verde.

---

## Phase 6: Incremento pós-clarificação — pulso "punchy", mini tremor e grade 30×30 (Priority: P1)

**Goal**: aplicar as clarificações de 2026-11-12: FR-002 revisado (pulso punchy), FR-015 (mini
tremor ao comer) e FR-014 (grade 30×30, casas de 48 px, janela 1440×1440).

**Independent Test**: abrir o jogo em 1440×1440 e comer frutas: placar salta, quica e pisca de
branco para amarelo; a tela dá um tremor curto (quickstart.md itens 0 e 5).

### Tests ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation.** Testes antigos que
> contradizem a spec revisada (amplitude do tremor em px; cobra inicial em (10,10) no `Flow`) DEVEM
> ser atualizados nesta fase, pois a spec mudou.

- [ ] T029 [P] [US1] Test in `tests/test_juice.py`: `ScorePulse` "punchy" — `scale == 1.8` at 60 ms, about 0.9 at 180 ms (the minimum), `scale == 1` and `flash == 0` at 300 ms; `warmth` goes 0 → 1 in the first 60 ms
- [ ] T030 [P] [US2] Rewrite shake tests in `tests/test_juice.py` for `ScreenShake.trigger(amplitude, duration_ms)` in cells: offset within the decaying amplitude, `done` with `offset == (0, 0)` at `duration_ms`; a new `trigger` replaces the running shake; `EAT_SHAKE` amplitude is a third of `COLLISION_SHAKE` and lasts 150 ms
- [ ] T031 [US1] Test in `tests/test_flow.py`: eating starts the eat shake (≤ 150 ms, then offset back to `(0, 0)`); colliding right after eating replaces it with the collision shake
- [ ] T032 Test in `tests/test_flow.py`: `Flow()` uses a 30 × 30 grid and the snake starts at `((15, 15), (14, 15), (13, 15))`; update `test_restart_starts_a_new_game` to the 30 × 30 start

### Implementation

- [ ] T033 [US1] Rework `ScorePulse` in `src/snake/juice.py`: three-segment scale (1.0→1.8 by 60 ms, →0.9 by 180 ms, →1.0 by 300 ms) and `warmth` (0→1 in 60 ms)
- [ ] T034 [US2] Make `ScreenShake` parametric in `src/snake/juice.py`: `trigger(amplitude, duration_ms)` in cells; constants `COLLISION_SHAKE = (1/3, 400)` and `EAT_SHAKE = (1/9, 150)`
- [ ] T035 [US1] In `src/snake/flow.py`: default grid 30 × 30; trigger `EAT_SHAKE` on eating and `COLLISION_SHAKE` on game over; update the shake every frame in all phases
- [ ] T036 In `src/snake/app.py`: `CELL = 48` (1440 × 1440 window), scale fonts, particles and score position by `CELL / 24`; shake offset multiplied by `CELL`; score flash blends white → yellow by `warmth`

**Checkpoint**: `pytest` verde; janela 1440×1440, pulso punchy e mini tremor ao comer.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T026 [P] Update `README.md` with the new screen flow (título → contagem → partida → fim)
- [X] T027 Measure frame time headlessly with 3 simultaneous bursts and confirm it stays within 60 fps (SC-004)
- [ ] T028 Run the full quickstart.md validation (pytest + manual checklist items 0–9) and record the result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories (o `Flow` é a base de todas)
- **User Stories (Phase 3–5)**: depend on Foundational; run in priority order P1 → P2 → P3,
  because all three edit `src/snake/flow.py` and `src/snake/app.py`
- **Incremento (Phase 6)**: depends on Phases 3–5 (altera pulso, tremor e o adaptador)
- **Polish (Phase 7)**: depends on all user stories, including Phase 6

### User Story Dependencies

- **US1 (P1)**: after Foundational; independent of US2/US3
- **US2 (P2)**: after Foundational; independent of US1 (shares only `juice.py`, different class)
- **US3 (P3)**: after Foundational; its menu phases wrap the `SHAKING` → menu step from US2 when both exist

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Princípio II)
- `juice.py` before `flow.py` before `app.py`
- Story complete (pytest verde + jogo abrindo) before the next priority (Princípio V)

### Parallel Opportunities

- T001 and T002 in parallel
- `test_juice.py` tasks ([P]) can be written alongside the `test_flow.py` task of the same story
- T012 and T017 (`juice.py` classes) are independent of `flow.py` work
- T029 and T030 (`test_juice.py`) can be written alongside T031–T032 (`test_flow.py`)

---

## Parallel Example: User Story 1

```bash
# Write US1 tests together (they must all fail first):
Task: "juice tests in tests/test_juice.py (T008, T009, T010)"
Task: "flow eat-effect test in tests/test_flow.py (T011)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational (jogo igual à 001, agora pelo `Flow`)
3. Phase 3: User Story 1
4. **STOP and VALIDATE**: `pytest` + quickstart.md itens 5 e 6

### Incremental Delivery

1. Setup + Foundational → mesmo jogo da 001 sobre o `Flow`
2. + US1 → partículas e pulso (MVP)
3. + US2 → tremor na colisão
4. + US3 → tela inicial, contagem e menu animado
5. Cada incremento termina jogável e com testes verdes

---

## Notes

- [P] tasks = different files or independent test functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
