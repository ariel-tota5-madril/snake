---

description: "Task list for 003-audio-sfx-bgm"
---

# Tasks: Áudio — efeitos sonoros e música 8-bit

**Input**: Design documents from `/specs/003-audio-sfx-bgm/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/audio-api.md, contracts/flow-api.md, quickstart.md

**Tests**: INCLUÍDOS. A constituição (Princípio II) exige test-first: cada teste DEVE ser escrito
e falhar antes da implementação correspondente. Os testes das features 001 e 002 DEVEM continuar
passando; os que dependem do menu de fim antigo ("Restart"/"Quit") DEVEM ser atualizados porque o
FR-016 mudou esse menu.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Paths seguem o layout `src/` + `tests/` do plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Módulos novos e a guarda de pureza

- [X] T001 [P] Create `src/snake/synth.py`, `src/snake/sounds.py`, `src/snake/settings.py` and `src/snake/audio.py` with module docstrings only
- [X] T002 [P] Extend `tests/test_core_purity.py` to assert `snake.synth`, `snake.sounds` and `snake.settings` import no `pygame`, `time` or `datetime`

**Checkpoint**: `pytest` verde; o jogo continua igual ao da 002.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: síntese, fila de eventos sonoros e o adaptador de áudio (com modo mudo), usados por
todas as histórias

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Write failing tests in `tests/test_synth.py`: `render()` length equals the sum of note durations at 22 050 Hz (±1 sample per note); all samples within [−32767, 32767]; first and last sample of each note close to 0 ("rampa de 2 ms"); `freq == 0` renders silence; `noise` is deterministic; `freq_end` slides pitch; `mix()` pads the shorter track and clips
- [X] T004 Implement `Note`, `render()` and `mix()` with `square50`, `square25`, `square12`, `triangle` and LFSR `noise` waves in `src/snake/synth.py`
- [X] T005 Write failing tests in `tests/test_flow.py`: `SoundEvent` exists with the members of data-model.md; `drain_sounds()` returns queued events in order and empties the queue
- [X] T006 Add `SoundEvent` enum and the event queue with `drain_sounds()` to `src/snake/flow.py`
- [X] T007 Implement `Audio.create(settings)` in `src/snake/audio.py` (`pre_init(22050, -16, 1, 512)`, 16 channels, music on a reserved channel) falling back to `SilentAudio` when the mixer fails; wire `src/snake/app.py` to build sounds once, create the audio and play `flow.drain_sounds()` every frame

**Checkpoint**: `pytest` verde; o jogo abre igual (ainda sem eventos sonoros); com `SDL_AUDIODRIVER=dummy` também.

---

## Phase 3: User Story 1 - Sons da jogabilidade (Priority: P1) 🎯 MVP

**Goal**: tique suave no passo, coleta, "pop" no pico do pulso e batida na colisão (FR-002 a FR-005).

**Independent Test**: jogar, comer e bater na parede ouvindo cada som (quickstart.md itens 6, 7, 11).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] [US1] Test in `tests/test_sounds.py`: `SFX` has `STEP`, `EAT`, `PULSE_POP` and `CRASH`; `STEP` has the lowest relative volume of all effects (FR-002) and lasts ≤ 30 ms; `EAT` rises in pitch; `CRASH` lasts about 350 ms
- [ ] T009 [P] [US1] Test in `tests/test_flow.py`: each step emits `STEP`; eating emits `EAT` in the same update as the burst; `PULSE_POP` is emitted 60 ms of game time after `EAT` ("PULSE_POP_DELAY_MS = 60"); game over emits `CRASH` together with the shake; turning emits nothing

### Implementation for User Story 1

- [ ] T010 [P] [US1] Define `STEP`, `EAT`, `PULSE_POP` and `CRASH` sounds with the relative volumes of research.md §5 in `src/snake/sounds.py`
- [ ] T011 [US1] Emit `STEP`, `EAT`, scheduled `PULSE_POP` and `CRASH` from `src/snake/flow.py`
- [ ] T012 [US1] Play effects in `src/snake/audio.py` at `relative volume × sfx/100`

**Checkpoint**: `pytest` verde; a partida tem tique, coleta, pop e batida.

---

## Phase 4: User Story 2 - Música de fundo (Priority: P2)

**Goal**: música da tela inicial e da partida em loop, jingles de derrota e vitória (FR-006, FR-007, FR-011).

**Independent Test**: abrir, jogar e perder ouvindo a música mudar (quickstart.md itens 1, 5, 11).

### Tests for User Story 2 ⚠️

- [ ] T013 [P] [US2] Test in `tests/test_sounds.py`: `MUSIC_TITLE` (120 BPM) and `MUSIC_GAME` (150 BPM) last a whole number of bars and start and end near 0 (loop sem estalo, SC-003); `JINGLES` has `LOSE` and `WIN`, each shorter than 2 s
- [ ] T014 [P] [US2] Test in `tests/test_flow.py`: `MUSIC_TITLE` on entering the title; `MUSIC_GAME` when the countdown ends; at the end of a game `MUSIC_STOP` then `LOSE` (collision, when the end menu opens) or `WIN` (victory)

### Implementation for User Story 2

- [ ] T015 [P] [US2] Compose the two original 3-voice loops (square melody, triangle bass, noise percussion) and the two jingles in `src/snake/sounds.py`
- [ ] T016 [US2] Emit `MUSIC_TITLE`, `MUSIC_GAME`, `MUSIC_STOP`, `LOSE` and `WIN` from `src/snake/flow.py`
- [ ] T017 [US2] Play music looped on the reserved channel at `MUSIC_GAIN (0,5) × music/100`, stop it on `MUSIC_STOP`, and play jingles in `src/snake/audio.py`

**Checkpoint**: `pytest` verde; músicas e jingles tocando nos momentos certos.

---

## Phase 5: User Story 4 - Pausa e opções de áudio (Priority: P2)

**Goal**: pausa no Esc com retomada em 1,5 s, menu "Jogar"/"Opções" na tela inicial, "Opções" no
fim de partida, tela de Opções com sliders salvos (FR-015 a FR-019).

**Independent Test**: pausar, abrir Opções, mudar volumes, voltar, continuar; reabrir o jogo e ver
os volumes mantidos (quickstart.md itens 1–4, 8–10, 12).

### Tests for User Story 4 ⚠️

- [ ] T018 [P] [US4] Tests in `tests/test_settings.py`: defaults 60/80; `adjust` moves by 10, stays within 0–100 and returns whether it changed; `save`/`load` round trip (creates the folder); missing file, invalid JSON, wrong types and out-of-range values all load as 60/80
- [ ] T019 [P] [US4] Rewrite `tests/test_menu.py` for the generic `Menu`: option sets `TITLE_OPTIONS`, `PAUSE_OPTIONS`, `END_OPTIONS` (`RESTART`, `OPTIONS`, `QUIT`) and `SETTINGS_OPTIONS`; `move_up`/`move_down` return whether the selection changed; no wrap-around
- [ ] T020 [US4] Tests in `tests/test_flow.py`: title menu (`PLAY` starts the countdown, `OPTIONS` opens Options); Options reachable from title, pause and end menu and "Voltar"/`escape()` returns to the same origin phase; ←/→ change the selected volume and leaving Options saves to `settings_path`; `escape()` in `PLAYING` pauses (`PAUSE_IN` → `PAUSE`), game and effects frozen; continue/`escape()` → `RESUME` with 3, 2, 1 every 500 ms, then `PLAYING` with the same snake and direction and no accumulated steps; pause → "Tela inicial" abandons the game and returns to the title with a fresh game; `escape()` is ignored in title, countdown, shaking and end menu; `MUSIC_DUCK`/`MUSIC_UNDUCK` around the pause
- [ ] T021 [US4] Update the 001/002 tests in `tests/test_flow.py` that assumed the end menu was ("Restart", "Quit") — ↓ now selects "Opções" (FR-016)

### Implementation for User Story 4

- [ ] T022 [P] [US4] Implement `AudioSettings` with `adjust`, `load` and `save` in `src/snake/settings.py`
- [ ] T023 [P] [US4] Generalize `src/snake/menu.py` into `Menu(options)` with the option sets above; keep `EndMenu` as `Menu(END_OPTIONS)`
- [ ] T024 [US4] In `src/snake/flow.py`: title menu, end menu with "Opções", phases `PAUSE_IN`/`PAUSE`/`PAUSE_OUT`/`RESUME`/`OPTIONS_IN`/`OPTIONS`/`OPTIONS_OUT` with origin tracking, `escape()`, ←/→ in Options, settings load/save, ducking events, frozen game time while paused
- [ ] T025 [US4] In `src/snake/app.py`: Esc → `escape()`; draw the title menu, pause menu, Options screen with two slider bars and "Voltar", and the resume countdown; default `settings_path` `~/.config/snake/settings.json`; apply volumes immediately and duck the music while paused in `src/snake/audio.py`

**Checkpoint**: `pytest` verde; pausa, Opções e volumes salvos funcionando.

---

## Phase 6: User Story 3 - Sons de interface e transições (Priority: P3)

**Goal**: bipes da contagem e da retomada, "vai!", navegação, confirmação e amostra de volume
(FR-008, FR-009, FR-010, FR-018).

**Independent Test**: começar pela tela inicial, navegar nos menus, ajustar Efeitos (quickstart.md itens 2, 3, 5, 9).

### Tests for User Story 3 ⚠️

- [ ] T026 [P] [US3] Test in `tests/test_sounds.py`: `SFX` has `COUNT`, `GO` (higher pitch and longer than `COUNT`), `NAV`, `CONFIRM` and `VOLUME_PREVIEW`
- [ ] T027 [P] [US3] Test in `tests/test_flow.py`: `COUNT` for each countdown and resume number and `GO` when the snake starts; `NAV` only when a menu selection or slider value changes; `CONFIRM` on accepted confirmations; `VOLUME_PREVIEW` when the Efeitos slider changes; ignored keys (arrows on title entrance, anything during countdown/shake/resume) emit nothing

### Implementation for User Story 3

- [ ] T028 [P] [US3] Define `COUNT`, `GO`, `NAV`, `CONFIRM` and `VOLUME_PREVIEW` sounds in `src/snake/sounds.py`
- [ ] T029 [US3] Emit `COUNT`, `GO`, `NAV`, `CONFIRM` and `VOLUME_PREVIEW` from `src/snake/flow.py`

**Checkpoint**: todas as histórias funcionando; `pytest` verde.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T030 [P] Update `README.md` with Esc/pause, the Options screen and where volumes are saved
- [ ] T031 Measure: building all sounds at startup takes < 2 s and the game keeps 60 fps with audio (SC-004)
- [ ] T032 Run the game loop with `SDL_AUDIODRIVER=dummy` and with the mixer forced to fail, confirming a full game completes silently (SC-005, FR-013)
- [ ] T033 Run the full quickstart.md validation (pytest + manual checklist items 1–13) and record the result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories
- **User Stories (Phase 3–6)**: depend on Foundational; run in order US1 → US2 → US4 → US3
  because they all edit `src/snake/flow.py`, and US3's menu sounds need the menus from US4
- **Polish (Phase 7)**: depends on all user stories

### User Story Dependencies

- **US1 (P1)**: after Foundational
- **US2 (P2)**: after Foundational; independent of US1 (different events)
- **US4 (P2)**: after Foundational; adds menus and phases that US3 makes audible
- **US3 (P3)**: after US4

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Princípio II)
- `synth`/`sounds`/`settings`/`menu` before `flow` before `audio`/`app`
- Story complete (pytest verde + jogo abrindo) before the next (Princípio V)

### Parallel Opportunities

- T001 and T002 in parallel
- `test_sounds.py`, `test_settings.py` and `test_menu.py` tasks can be written alongside the `test_flow.py` task of the same story
- `sounds.py`, `settings.py` and `menu.py` implementation tasks ([P]) are independent of `flow.py`

---

## Parallel Example: User Story 4

```bash
# Write US4 tests together (they must all fail first):
Task: "settings tests in tests/test_settings.py (T018)"
Task: "generic menu tests in tests/test_menu.py (T019)"
Task: "pause/options flow tests in tests/test_flow.py (T020, T021)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational (síntese + fila de eventos + áudio com modo mudo)
3. Phase 3: User Story 1
4. **STOP and VALIDATE**: `pytest` + quickstart.md itens 6, 7, 11

### Incremental Delivery

1. Setup + Foundational → jogo igual, com áudio pronto para tocar
2. + US1 → sons da partida (MVP)
3. + US2 → músicas e jingles
4. + US4 → pausa e Opções com volumes salvos
5. + US3 → sons de interface
6. Cada incremento termina jogável e com testes verdes

---

## Notes

- [P] tasks = different files or independent test functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
