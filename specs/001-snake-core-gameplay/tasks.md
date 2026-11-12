---

description: "Task list for 001-snake-core-gameplay"
---

# Tasks: Núcleo do Snake — movimento, comida e pontuação

**Input**: Design documents from `/specs/001-snake-core-gameplay/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/core-api.md, quickstart.md

**Tests**: INCLUÍDOS. A constituição (Princípio II) exige test-first para toda regra: cada teste
DEVE ser escrito e falhar antes da implementação correspondente.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths seguem o layout `src/` + `tests/` do plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create package skeleton `src/snake/__init__.py`, empty `src/snake/core.py` and `tests/` per plan.md
- [X] T002 Create `requirements.txt` with `pygame>=2.6` and `pytest>=8`, then install into `.venv`
- [X] T003 [P] Create `pyproject.toml` with pytest config (`pythonpath = ["src"]`, `testpaths = ["tests"]`)

**Checkpoint**: `pytest` runs (0 tests) without errors.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tipos e estado inicial do núcleo, usados por todas as histórias

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Write failing test for the initial state in `tests/test_movement.py`: grade 20 × 20, `snake == ((10,10), (9,10), (8,10))`, `direction == RIGHT`, `score == 0`, `status == RUNNING`
- [X] T005 Implement `Direction` (`UP (0,-1)`, `DOWN (0,1)`, `LEFT (-1,0)`, `RIGHT (1,0)`) and `Status` (`RUNNING`, `GAME_OVER`, `WON`) enums in `src/snake/core.py`
- [X] T006 Implement `Game.__init__(width=20, height=20, rng=None, seed=None)` in `src/snake/core.py` creating the initial state (rng = given `random.Random` or `random.Random(seed)`; `food` temporarily `None`) until T004 passes
- [X] T007 Create minimal Pygame adapter `src/snake/app.py` (opens a 20 × 20 grid window, draws the snake from `Game`, closes on window exit) and entry point `src/snake/__main__.py`

**Checkpoint**: `pytest` verde e `python -m snake` abre a janela com a cobra parada (Princípio V).

---

## Phase 3: User Story 1 - Mover a cobra pela grade (Priority: P1) 🎯 MVP

**Goal**: cobra avança uma casa por passo, muda de direção pelas setas e a partida termina ao
bater na parede ou no próprio corpo.

**Independent Test**: iniciar o jogo, ver a cobra andar, virar com as setas e bater na parede
(quickstart.md itens 1, 2, 3, 5 e 6).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Test in `tests/test_movement.py`: `step()` without input moves the head one cell right and keeps length 3
- [X] T009 [P] [US1] Test in `tests/test_movement.py`: `turn(UP)` then `step()` moves up; `turn(LEFT)` while going right is ignored
- [X] T010 [P] [US1] Test in `tests/test_movement.py`: two `turn()` calls in the same step apply only the first valid one ("no máximo um comando por passo (FR-005)") and the snake never reverses onto itself
- [X] T011 [P] [US1] Test in `tests/test_collision.py`: head leaving the grid sets `status == GAME_OVER` and the snake does not move out of the grid
- [X] T012 [P] [US1] Test in `tests/test_collision.py`: head entering its own body sets `GAME_OVER`; moving into the cell the tail just left is allowed
- [X] T013 [P] [US1] Test in `tests/test_collision.py`: after `GAME_OVER`, `step()` and `turn()` change nothing (FR-013)

### Implementation for User Story 1

- [X] T014 [US1] Implement `Game.turn(direction)` in `src/snake/core.py`: ignore opposite of current direction, keep only the first valid command per step, no effect outside `RUNNING`
- [X] T015 [US1] Implement `Game.step()` in `src/snake/core.py` following data-model.md steps 1–4, 6 and 7 (apply pending, move, wall and body collision with tail freed, freeze when not `RUNNING`)
- [X] T016 [US1] Wire arrow keys to `turn()` and a fixed 8 steps/s clock to `step()` in `src/snake/app.py`; show a "Game Over" message when `status == GAME_OVER`

**Checkpoint**: `pytest` verde; a cobra anda, vira e a partida termina na parede e no corpo.

---

## Phase 4: User Story 2 - Comer a comida e crescer (Priority: P2)

**Goal**: sempre há uma comida em casa livre; comer faz a cobra crescer e gera outra comida de
forma reproduzível.

**Independent Test**: levar a cobra até a comida e ver o crescimento e a nova comida
(quickstart.md item 4).

### Tests for User Story 2 ⚠️

- [X] T017 [P] [US2] Test in `tests/test_food.py`: a new game has exactly one food, inside the grid and not on the snake
- [X] T018 [P] [US2] Test in `tests/test_food.py`: with food right in front of the head, `step()` grows the snake by 1 and spawns a new food on a free cell
- [X] T019 [P] [US2] Test in `tests/test_food.py`: two games with the same seed and the same `turn`/`step` sequence produce identical `food` sequences (FR-008, SC-004)
- [X] T020 [P] [US2] Test in `tests/test_collision.py`: on a grid filled by the snake after eating, `status == WON` and `food is None` (FR-012)

### Implementation for User Story 2

- [X] T021 [US2] Implement food spawn in `src/snake/core.py`: `rng.choice` over the sorted list of free cells; call it in `Game.__init__`
- [X] T022 [US2] Extend `Game.step()` in `src/snake/core.py` with data-model.md steps 5 and 8 (eat → grow, keep tail, respawn food; no free cell → `WON`)
- [X] T023 [US2] Draw the food in `src/snake/app.py` and show a "Você venceu" message when `status == WON`

**Checkpoint**: `pytest` verde; a cobra come, cresce e a comida reaparece.

---

## Phase 5: User Story 3 - Acompanhar a pontuação (Priority: P3)

**Goal**: pontuação visível, começando em 0 e subindo 1 por comida.

**Independent Test**: comer comidas e conferir a pontuação na tela (quickstart.md itens 1 e 4).

### Tests for User Story 3 ⚠️

- [X] T024 [P] [US3] Test in `tests/test_score.py`: score starts at 0, goes +1 per food eaten and does not change on moves without food

### Implementation for User Story 3

- [X] T025 [US3] Increment `score` when food is eaten in `Game.step()` in `src/snake/core.py`
- [X] T026 [US3] Render the current score during play and the final score on game over in `src/snake/app.py`

**Checkpoint**: todas as histórias funcionando; `pytest` verde.

---

## Phase 6: User Story 1 (incremento) - Fim de partida: menu e reinício (Priority: P1)

**Goal**: ao fim da partida (Game Over ou vitória), mostrar a pontuação final e o menu
"Restart"/"Quit"; ↑/↓ escolhem e Espaço/Enter confirmam (FR-014, FR-015, FR-016). Adicionado
após a clarificação de 2026-11-12.

**Independent Test**: perder uma partida, escolher "Restart" e jogar de novo; perder outra e
escolher "Quit" (quickstart.md itens 7 a 10).

### Tests for User Story 1 (incremento) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US1] Test in `tests/test_restart.py`: after `GAME_OVER`, `restart()` returns to the initial state (`snake == ((10,10), (9,10), (8,10))`, `direction == RIGHT`, `score == 0`, `status == RUNNING`) with one food on a free cell
- [ ] T031 [P] [US1] Test in `tests/test_restart.py`: `restart()` also works after `WON`, and two sessions with the same seed and the same commands (including a restart) produce the same food sequence (mesmo RNG)
- [ ] T032 [P] [US1] Test in `tests/test_menu.py`: `EndMenu` starts with `selected == RESTART`; `move_down()` selects `QUIT`; `move_down()` at `QUIT` and `move_up()` at `RESTART` change nothing ("sem volta circular"); `confirm()` returns the selected option
- [ ] T033 [P] Extend `tests/test_core_purity.py` to also check that `snake.menu` imports no `pygame`, `time` or `datetime`

### Implementation for User Story 1 (incremento)

- [ ] T034 [US1] Implement `Game.restart()` in `src/snake/core.py`: reset snake, direction, pending, score and status as in `__init__`, then spawn food with the same `rng`
- [ ] T035 [P] [US1] Implement `MenuOption` (`RESTART`, `QUIT`) and `EndMenu` (`options`, `selected`, `move_up()`, `move_down()`, `confirm()`) in `src/snake/menu.py`
- [ ] T036 [US1] In `src/snake/app.py`: when `status` is not `RUNNING`, show final score and the menu with the selected option highlighted; route ↑/↓ to the menu and Espaço/Enter to `confirm()` (`RESTART` → `game.restart()`, `QUIT` → close); ignore Espaço/Enter while `RUNNING`

**Checkpoint**: `pytest` verde; perder → "Restart" inicia nova partida; "Quit" fecha o jogo.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T027 [P] Add a test in `tests/test_core_purity.py` asserting `snake.core` does not import `pygame` (Princípio I)
- [X] T028 [P] Write `README.md` with setup, `pytest` and `python -m snake` instructions
- [ ] T029 Run the full quickstart.md validation (pytest + manual checklist items 1–10) and record the result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories
- **User Stories (Phase 3–5)**: depend on Foundational; run in priority order P1 → P2 → P3
  because all three edit `Game.step()` in `src/snake/core.py`
- **US1 incremento (Phase 6)**: depends on Phases 3–5 (reinício precisa do estado completo:
  comida e pontuação)
- **Polish (Phase 7)**: depends on all user stories, including Phase 6

### User Story Dependencies

- **US1 (P1)**: after Foundational; no dependency on other stories
- **US2 (P2)**: after Foundational; extends `step()` from US1 (same file)
- **US3 (P3)**: after US2, since scoring happens in the eat branch of `step()`

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Princípio II)
- Core (`core.py`) before adapter (`app.py`)
- Story complete (pytest verde + jogo abrindo) before the next priority (Princípio V)

### Parallel Opportunities

- T003 can run alongside T001–T002
- All test tasks inside a story ([P]) can be written together: they touch separate test functions
- T027 and T028 can run in parallel
- T030–T033 (tests) can be written together; T035 (`menu.py`) can run alongside T034 (`core.py`)

---

## Parallel Example: User Story 1

```bash
# Write all US1 tests together (they must all fail first):
Task: "Movement tests in tests/test_movement.py (T008, T009, T010)"
Task: "Collision tests in tests/test_collision.py (T011, T012, T013)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: User Story 1
4. **STOP and VALIDATE**: `pytest` + quickstart.md itens 1, 2, 3, 5 e 6
5. Demo: cobra controlável que termina ao bater

### Incremental Delivery

1. Setup + Foundational → janela com a cobra parada
2. + US1 → cobra jogável com game over (MVP)
3. + US2 → comida e crescimento
4. + US3 → pontuação
5. Cada incremento termina jogável e com testes verdes

---

## Notes

- [P] tasks = different files or independent test functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
