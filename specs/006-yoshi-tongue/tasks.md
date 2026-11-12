---

description: "Task list for 006-yoshi-tongue"
---

# Tasks: Língua de Yoshi — habilidade com cooldown

**Input**: Design documents from `/specs/006-yoshi-tongue/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tongue-api.md, quickstart.md

**Tests**: INCLUÍDOS (Princípio II: test-first). Os testes das features 001–005 DEVEM continuar
passando; Espaço continua confirmando fora da partida.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 [P] Create `src/snake/tongue.py` with the module docstring and the constants `COOLDOWN_MS = 8000`, `REACH = 3`, `ANIM_MS = 300`
- [X] T002 [P] Extend `tests/test_core_purity.py` to assert `snake.tongue` imports no `pygame`, `time` or `datetime`

**Checkpoint**: `pytest` verde; jogo igual.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a regra do disparo no núcleo, usada por todas as histórias

- [X] T003 Write failing tests in `tests/test_tongue.py` for `Game.tongue(reach=3)`: food at distance 1, 2 and 3 straight ahead is eaten (`ate`, `target`, `reach == distance`, score +1, new food not on the snake); food at distance 4 is not eaten (`reach == 3`); a wall stops the tongue (`reach` = free cells before it); a body segment between head and food blocks it; the direction used is the current `game.direction` even with a turn queued; after eating, the next `step()` grows the snake by 1 (tail stays) and the one after does not; eating the last free cell wins; with `status != RUNNING` returns `reach=0, ate=False`
- [X] T004 Implement `TongueShot`, `Game.tongue()` and the pending growth (`_grow`, consumed in `step()`, cleared in `restart()`) in `src/snake/core.py`

**Checkpoint**: `pytest` verde.

---

## Phase 3: User Story 1 - Atirar a língua e comer à distância (Priority: P1) 🎯 MVP

**Goal**: Espaço dispara a língua na partida; come a fruta ao alcance; recarga de 8 s gasta mesmo errando; bloqueada no Frenzy; recarga para fora de `PLAYING` (FR-001 a FR-006, FR-011, FR-013, FR-014).

**Independent Test**: quickstart.md itens 2, 3, 5, 6, 7, 9, 10.

### Tests for User Story 1 ⚠️

- [X] T005 [P] [US1] Write failing tests in `tests/test_tongue.py` for `Tongue`: starts ready (`progress == 1`); `fire` sets `remaining_ms = 8000`, `ready` False, `progress` 0; `update_cooldown` returns True only on the update it becomes ready, never goes below 0; `extension` goes 0 → 1 at 150 ms → 0 at 300 ms and stays 0; `shot` keeps the last `TongueShot`
- [X] T006 [US1] Write failing tests in `tests/test_flow.py`: `space()` in PLAYING with the food 2 cells ahead eats it (score +1, burst, pulse, `EAT`, `TONGUE`, later `PULSE_POP`); a second `space()` right after does nothing (no sound); a miss also starts the 8 s cooldown; the cooldown advances only in PLAYING (unchanged across pause/resume and countdown); `space()` outside PLAYING behaves as `confirm()` (title, menus); during the Feeding Frenzy `tongue_locked` is True and `space()` does nothing; Restart and "Tela inicial" give a ready tongue; eating with the tongue at score 9 starts the Frenzy; same seed + same inputs → same result

### Implementation for User Story 1

- [X] T007 [US1] Implement `Tongue` (`fire`, `update_cooldown`, `update_anim`, `ready`, `progress`, `extension`, `shot`) in `src/snake/tongue.py`
- [X] T008 [US1] Implement in `src/snake/flow.py`: `tongue`, `tongue_locked`, `space()`, the shared eat effects helper (used by steps and tongue, including the Frenzy threshold), cooldown updated only in `_update_playing`, tongue animation in `_update_effects`, reset on restart/title; add `SoundEvent.TONGUE`
- [X] T009 [US1] In `src/snake/app.py`: Space calls `flow.space()` (outside the name entry); draw the tongue from the head in `shot.direction` with length `reach × extension`, and a ghost fruit at the tip while retracting when `ate`

**Checkpoint**: língua jogável (sem ícone e sem sons novos); `pytest` verde.

---

## Phase 4: User Story 2 - Ícone com recarga em forma de relógio (Priority: P1)

**Goal**: ícone fixo no canto inferior esquerdo (~2 casas): relógio que se ilumina na recarga, pulso + "pronto", brilho contínuo, acinzentado no Frenzy, aviso adiado (FR-007 a FR-010, FR-005).

**Independent Test**: quickstart.md itens 1, 4, 8.

### Tests for User Story 2 ⚠️

- [X] T010 [US2] Write failing tests in `tests/test_flow.py`: when the cooldown ends in normal play, `TONGUE_READY` is emitted once and `icon_pulse` triggers; no `TONGUE_READY` at the start of a game or after restart; if the cooldown ends during the Frenzy, no `TONGUE_READY` until the Frenzy ends, then exactly one when play resumes; a timeout/collision ending the Frenzy does not announce

### Implementation for User Story 2

- [X] T011 [US2] Implement the ready announcement (`_ready_announced`, `icon_pulse`, deferral while locked) and add `SoundEvent.TONGUE_READY` in `src/snake/flow.py`
- [X] T012 [US2] Draw the icon in `src/snake/app.py`: bottom-left, ~2 cells, 16 px margin; recharging = dark version + light clockwise wedge from the top proportional to `progress`; ready = full color with `icon_pulse` scale and a soft sinusoidal halo (~1.2 s); locked = grayscale without pulse/halo; visible only during the match

**Checkpoint**: ícone completo; `pytest` verde.

---

## Phase 5: User Story 3 - Sons da língua (Priority: P2)

**Goal**: "tchum" no disparo e o "pronto" (FR-009, FR-012).

### Tests for User Story 3 ⚠️

- [X] T013 [US3] Write failing tests in `tests/test_sounds.py`: `SFX` has `TONGUE` (~120 ms, descending pitch, clean edges) and `TONGUE_READY` (~160 ms, ascending, clean edges)

### Implementation for User Story 3

- [X] T014 [US3] Synthesize `TONGUE` and `TONGUE_READY` in `src/snake/sounds.py` (research.md §5)

**Checkpoint**: todas as histórias; `pytest` verde.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 [P] Update `README.md` (Espaço = língua, alcance, recarga, Frenzy)
- [X] T016 Render frames (tongue out, icon recharging/ready/locked) and measure frame time with the headless drive (SC-005)
- [ ] T017 Run the quickstart.md validation (manual, by the user)

---

## Dependencies & Execution Order

- Setup → Foundational → US1 → US2 → US3 → Polish
- US2 depende de US1 (o ícone mostra o estado da `Tongue`); US3 depende de US1/US2 (eventos `TONGUE` e `TONGUE_READY`)
- Dentro de cada história: testes falhando → `core.py`/`tongue.py` → `flow.py` → `app.py`

### Parallel Opportunities

- T001 e T002
- T005 (test_tongue.py) com T006 (test_flow.py)

## Parallel Example: User Story 1

```bash
Task: "T005 Tongue cooldown tests in tests/test_tongue.py"
Task: "T006 Flow tongue tests in tests/test_flow.py"
```

## Implementation Strategy

1. Setup + Foundational (regra no núcleo)
2. US1 → língua jogável (MVP)
3. US2 → ícone
4. US3 → sons
5. Polish

## Notes

- Commit ao fim de cada fase; `pytest` verde e jogo abrindo em todo checkpoint (Princípio V)
