---

description: "Task list for 005-highscore-table"
---

# Tasks: Highscore — nome do jogador e placar animado

**Input**: Design documents from `/specs/005-highscore-table/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/highscores-api.md, contracts/flow-api.md, quickstart.md

**Tests**: INCLUÍDOS (Princípio II: test-first). Os testes das features 001–004 que passam pela
tela inicial ou pelo menu de fim DEVEM ser ajustados: "Jogar" agora abre a entrada de nome, e o
menu de fim (Restart/Opções/Quit) virou o placar com "Jogar de novo"/"Tela inicial" (FR-005,
FR-010, FR-010a).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3, US4

---

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 [P] Create `src/snake/highscores.py` and `src/snake/scoreboard.py` with module docstrings only
- [ ] T002 [P] Extend `tests/test_core_purity.py` to assert `snake.highscores` and `snake.scoreboard` import no `pygame`, `time` or `datetime`

**Checkpoint**: `pytest` verde; jogo igual ao da 004.

---

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T003 Write failing tests in `tests/test_juice.py`: `ParticleBurst(..., angle=(lo, hi))` creates particles whose velocity angles are within the range; default still covers all directions
- [ ] T004 Implement the `angle` parameter of `ParticleBurst` in `src/snake/juice.py`

**Checkpoint**: `pytest` verde.

---

## Phase 3: User Story 1 - Nome do jogador antes da partida (Priority: P1) 🎯 MVP

**Goal**: "Jogar" abre a entrada de nome (até 10 caracteres); Enter com nome válido inicia a contagem; Esc volta; nome lembrado na sessão; tela inicial com "Sair"; WASD como setas fora da entrada de nome (FR-001 a FR-004, FR-010a, FR-011).

**Independent Test**: quickstart.md itens 1–3, 12, 14, 15.

### Tests for User Story 1 ⚠️

- [ ] T005 [P] [US1] Write failing tests in `tests/test_menu.py`: `TITLE_OPTIONS == (PLAY, OPTIONS, QUIT)` with QUIT labeled "Sair"; `NameEntry` accepts ASCII letters, digits and space up to 10 chars (returns False beyond the limit or for other chars), `backspace` returns False when empty, `value` strips spaces, `confirmable` is False for empty/only spaces, `initial` prefills
- [ ] T006 [US1] Write failing tests in `tests/test_flow.py` and update the helpers (`to_playing`, `advance_through_title`, `sounds_until`, `to_title`-based tests) to go through the name entry: confirming PLAY goes TITLE_OUT → NAME_IN → NAME (`accepts_text`); `type_text`/`backspace` edit and emit `NAME_TYPE` only when the text changes; Enter with empty name does nothing (no sound); Enter with a name emits `CONFIRM`, goes NAME_OUT → COUNTDOWN and sets `player_name`; Esc in NAME returns to TITLE_IN without `MUSIC_TITLE`; the name entry reopens prefilled; QUIT on the title requests quit with `CONFIRM`

### Implementation for User Story 1

- [ ] T007 [US1] Implement `NameEntry`, `MenuOption.QUIT = "Sair"` and the new `TITLE_OPTIONS` in `src/snake/menu.py`
- [ ] T008 [US1] Implement the `NAME_IN`/`NAME`/`NAME_OUT` phases, `type_text`, `backspace`, `accepts_text`, `player_name` and title QUIT in `src/snake/flow.py`; add `NAME_TYPE` to `SoundEvent`
- [ ] T009 [US1] Synthesize `NAME_TYPE` in `src/snake/sounds.py` (with a test in `tests/test_sounds.py`)
- [ ] T010 [US1] In `src/snake/app.py`: draw the name entry panel (label, field with blinking cursor, hint); send `event.unicode` / Backspace while `flow.accepts_text`; map W/A/S/D to directions otherwise

**Checkpoint**: nome antes de cada partida; Sair na tela inicial; WASD; `pytest` verde.

---

## Phase 4: User Story 2 - Placar de highscore no fim da partida (Priority: P1)

**Goal**: placar vertical das 10 melhores, salvo/carregado, 5 linhas com rolagem, quem não entra aparece abaixo, opções "Jogar de novo"/"Tela inicial" (FR-005 a FR-010). Sem foguete ainda: o resultado já aparece no lugar.

**Independent Test**: quickstart.md itens 4–7, 10, 13, 16 (sem a animação).

### Tests for User Story 2 ⚠️

- [ ] T011 [P] [US2] Write failing tests in `tests/test_highscores.py`: `rank_for`/`insert` on empty, partial and full tables; ties put the newcomer below; full table drops the 10th; non-qualifying returns None and leaves the table unchanged; same name repeats; `save` + `load` round-trip (creates folder); missing file, invalid JSON, non-list, and entries with bad name/score are tolerated (bad entries dropped, rest sorted and capped)
- [ ] T012 [P] [US2] Write failing tests in `tests/test_scoreboard.py` for the static board: non-qualifying → `done` immediately, `outside` set, `view_top` at the end of the list; `rows()` lists the entries at their lines; `scroll` moves one line within [0, N − 5] and returns False at the limits; `scroll` is ignored while not done
- [ ] T013 [US2] Write failing tests in `tests/test_flow.py` (and update end-menu tests in `tests/test_flow.py` / `tests/test_menu.py`): `END_OPTIONS == (PLAY_AGAIN, TITLE)`; game over / win / Frenzy timeout insert the result and save it to `highscores_path`; MENU shows `scoreboard`; once done, ↑/↓ scroll with NAV, ←/→ switch options with NAV; "Jogar de novo" restarts to COUNTDOWN without the name entry; "Tela inicial" and Esc go to TITLE_IN with `MUSIC_TITLE` and a fresh game; a Flow created with the same path loads the saved table

### Implementation for User Story 2

- [ ] T014 [US2] Implement `Entry` and `Highscores` in `src/snake/highscores.py`
- [ ] T015 [US2] Implement the static part of `Scoreboard` (`rows`, `view_top`, `scroll`, `outside`, `done`) in `src/snake/scoreboard.py`
- [ ] T016 [US2] Update `src/snake/menu.py` (`PLAY_AGAIN`, `END_OPTIONS`, `EndMenu`) and `src/snake/flow.py` (`highscores_path`, insert+save at game end, scoreboard in MENU, new MENU inputs and exits, Options no longer reachable from the end screen)
- [ ] T017 [US2] Draw the vertical scoreboard panel in `src/snake/app.py` (title, 5 clipped lines with rank/name/score in fixed-width characters, ▲/▼ indicators, outside result, side-by-side options) and pass `HIGHSCORES_PATH`

**Checkpoint**: placar jogável de ponta a ponta, sem animação; `pytest` verde.

---

## Phase 5: User Story 3 - Animação de foguete subindo o placar (Priority: P2)

**Goal**: ignição com tremor e chama, expulsão do antigo 10º, subida com aceleração e câmera seguindo, nomes explodindo e se remontando abaixo, pouso, "1ST PLACE!", Enter pula (FR-012 a FR-016).

**Independent Test**: quickstart.md itens 4, 8, 9, 11.

### Tests for User Story 3 ⚠️

- [ ] T018 [P] [US3] Write failing tests in `tests/test_scoreboard.py` for `Shatter`: offsets start at 0, spread during the scatter phase, return to 0 at the end of reform while `base_y` goes from `from_y` to `to_y`; expelled shatter falls (dy grows) and fades; done times 650/800 ms; deterministic with the same seed
- [ ] T019 [US3] Write failing tests in `tests/test_scoreboard.py` for the rocket: starts at the bottom line in IGNITION with jitter and flame bursts, `"ignite"` event; full table → expelled shatter + `"hit"` at ignition; CLIMB after 700 ms with `"launch"`, speed reaches 5 lines/s and stays there; camera: rocket screen position stops at 1.6 while `view_top > 0`, then view stays 0 and the rocket keeps moving at max speed; each passed entry emits `"hit"` when `rocket_y <= k + 0.5` and becomes a shatter to line `k + 1`; LANDING with `"land"`; rank 0 → FIRST_PLACE with `"first"` and `first_place` rising to 1; total ≤ 5 s for the worst case; `skip()` reaches the same final state without extra events; same seed → same animation
- [ ] T020 [US3] Write failing tests in `tests/test_flow.py`: in MENU, Enter during the animation skips it (no CONFIRM) and a second Enter confirms the option; arrows are ignored during the animation; scoreboard events become `ROCKET_IGNITE`, `ROCKET_LAUNCH`, `ROCKET_HIT`, `ROCKET_LAND`, `FIRST_PLACE` sound events

### Implementation for User Story 3

- [ ] T021 [US3] Implement `Shatter` and the rocket timeline, camera, impacts, flame, first place and `skip` in `src/snake/scoreboard.py`
- [ ] T022 [US3] Wire skip, event draining and the new `SoundEvent` members in `src/snake/flow.py`
- [ ] T023 [US3] Draw the rocket name (jitter, highlight), flame particles, shattered characters, camera offset and "1ST PLACE!" in `src/snake/app.py`

**Checkpoint**: animação completa; `pytest` verde.

---

## Phase 6: User Story 4 - Sons do placar (Priority: P3)

**Goal**: ignição, decolagem, impacto, pouso e fanfarra (FR-017).

### Tests for User Story 4 ⚠️

- [ ] T024 [US4] Write failing tests in `tests/test_sounds.py`: `ROCKET_IGNITE`, `ROCKET_LAUNCH`, `ROCKET_HIT`, `ROCKET_LAND` in `SFX` with durations from research.md §7 and clean edges; `FIRST_PLACE` in `JINGLES`

### Implementation for User Story 4

- [ ] T025 [US4] Synthesize the rocket sounds and the first-place fanfare in `src/snake/sounds.py`

**Checkpoint**: todas as histórias; `pytest` verde.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Update `README.md` (name entry, highscores file, controls with WASD, Sair)
- [ ] T027 Measure frame time during the scoreboard animation with the headless drive (SC-004) and render frames to check the layout
- [ ] T028 Run the quickstart.md validation (manual, by the user)

---

## Dependencies & Execution Order

- Setup → Foundational → US1 → US2 → US3 → US4 → Polish
- US2 depende de US1 (o nome do jogador entra no placar); US3 depende de US2 (anima o placar);
  US4 depende de US3 (os eventos sonoros vêm da animação)
- Dentro de cada história: testes falhando → módulos puros → `flow.py` → `app.py`

### Parallel Opportunities

- T001 e T002; T005 com T006 (arquivos diferentes, mas T006 depende dos nomes de T005 só na implementação)
- T011 e T012; T018 antes de T019 no mesmo arquivo

## Implementation Strategy

1. US1 → já dá para jogar com nome (MVP)
2. US2 → placar salvo e navegável
3. US3 → foguete
4. US4 → sons
5. Polish

## Notes

- Commit ao fim de cada fase; `pytest` verde e jogo abrindo em todo checkpoint (Princípio V)
