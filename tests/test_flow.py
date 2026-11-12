from snake.core import Direction, Game, Status
from snake.flow import STEP_MS, Flow, Phase
from snake.menu import MenuOption

MENU_PHASES = {Phase.MENU_IN, Phase.MENU}


def to_playing(flow: Flow) -> Flow:
    """Avança pelas telas (inicial, contagem) até a partida começar."""
    for _ in range(1000):
        if flow.phase is Phase.PLAYING:
            return flow
        if flow.phase is Phase.TITLE:
            flow.confirm()
        flow.update(50)
    raise AssertionError(f"não chegou em PLAYING (fase {flow.phase})")


def to_menu(flow: Flow) -> Flow:
    """Deixa a cobra bater na parede e avança até o menu estar aceitando teclas."""
    flow.game.food = (0, 0)
    for _ in range(1000):
        if flow.phase is Phase.MENU:
            return flow
        flow.update(50)
    raise AssertionError(f"não chegou em MENU (fase {flow.phase})")


# T003
def test_playing_steps_once_per_step_ms():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    head = flow.game.snake[0]
    flow.update(STEP_MS - 1)
    assert flow.game.snake[0] == head
    flow.update(1)
    assert flow.game.snake[0] == (head[0] + 1, head[1])


def test_direction_turns_snake_while_playing():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    flow.direction(Direction.UP)
    flow.update(STEP_MS)
    assert flow.game.direction is Direction.UP


def test_confirm_is_ignored_while_playing():
    flow = to_playing(Flow(seed=1))
    snapshot = (flow.phase, flow.game.snake, flow.game.score)
    flow.confirm()
    assert (flow.phase, flow.game.snake, flow.game.score) == snapshot


# T004
def test_game_over_leads_to_menu():
    flow = to_menu(to_playing(Flow(seed=1)))
    assert flow.game.status is Status.GAME_OVER
    assert flow.menu is not None
    assert flow.menu.selected is MenuOption.RESTART


def advance_through_title(flow: Flow) -> Flow:
    """Passa pela tela inicial e pela contagem sem exigir que a fase PLAYING seja observada."""
    flow.update(UI_ANIM_MS)
    flow.confirm()
    flow.update(UI_ANIM_MS)
    return flow


def test_win_leads_to_menu():
    flow = advance_through_title(Flow(seed=1, width=4, height=1))
    assert flow.game.food == (3, 0)  # única casa livre: o primeiro passo vence
    for _ in range(1000):
        if flow.phase is Phase.MENU:
            break
        flow.update(50)
    assert flow.game.status is Status.WON
    assert flow.menu is not None


def test_menu_selection_moves_with_up_and_down():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.direction(Direction.DOWN)
    assert flow.menu.selected is MenuOption.OPTIONS  # 003/FR-016: Restart, Opções, Quit
    flow.direction(Direction.UP)
    assert flow.menu.selected is MenuOption.RESTART


def test_restart_starts_a_new_game():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.confirm()
    while flow.phase is not Phase.COUNTDOWN:
        flow.update(50)
    assert flow.game.status is Status.RUNNING
    assert flow.game.snake == ((15, 15), (14, 15), (13, 15))
    assert flow.game.score == 0
    assert flow.menu is None
    to_playing(flow)  # e a nova partida de fato começa


def test_quit_option_requests_quit():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.direction(Direction.DOWN)
    flow.direction(Direction.DOWN)  # 003/FR-016: Quit é a terceira opção
    flow.confirm()
    assert flow.quit_requested


def test_quit_works_in_any_phase():
    flow = Flow(seed=1)
    flow.quit()
    assert flow.quit_requested


# T005 (SC-005)
def test_flow_keeps_the_same_food_sequence_as_a_bare_game():
    def foods_of(game_like_step, game) -> list:
        foods = [game.food]
        for _ in range(60):
            if game.status is not Status.RUNNING:
                break
            hx, hy = game.snake[0]
            fx, fy = game.food
            command = (Direction.RIGHT if fx > hx else Direction.LEFT) if fx != hx else (
                Direction.DOWN if fy > hy else Direction.UP)
            game_like_step(command)
            foods.append(game.food)
        return foods

    bare = Game(seed=11, width=30, height=30)  # o jogo da 002 usa grade 30x30 (FR-014)
    bare.step()  # o Flow dá o primeiro passo assim que a contagem termina (SC-003)

    def bare_step(command):
        bare.turn(command)
        bare.step()

    flow = to_playing(Flow(seed=11))

    def flow_step(command):
        flow.direction(command)
        flow.update(STEP_MS)

    assert foods_of(flow_step, flow.game) == foods_of(bare_step, bare)


# T011
def test_eating_spawns_burst_at_head_and_triggers_pulse():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    assert flow.game.score == 1
    assert len(flow.bursts) == 1
    burst = flow.bursts[0]
    assert burst.origin == (hx + 1, hy)
    assert flow.pulse.scale > 1 or flow.pulse.flash > 0


def test_moving_without_eating_spawns_nothing():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    flow.update(STEP_MS)
    assert flow.bursts == []
    assert flow.pulse.flash == 0


def test_effects_keep_updating_after_game_over():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    assert len(flow.bursts) == 1
    to_menu(flow)
    for _ in range(20):
        flow.update(50)
    assert flow.bursts == []


# T016
def test_game_over_shakes_before_showing_the_menu():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    while flow.phase is Phase.PLAYING:
        flow.update(STEP_MS)
    assert flow.game.status is Status.GAME_OVER
    assert flow.phase is Phase.SHAKING
    assert flow.menu is None
    flow.direction(Direction.DOWN)  # ignorado durante o tremor
    flow.confirm()
    assert flow.phase is Phase.SHAKING and not flow.quit_requested
    flow.update(399)
    assert flow.phase is Phase.SHAKING
    flow.update(1)
    assert flow.shake.offset == (0, 0)
    assert flow.phase is not Phase.SHAKING
    assert flow.menu is not None and flow.menu.selected is MenuOption.RESTART


def test_win_goes_to_menu_without_shaking():
    flow = advance_through_title(Flow(seed=1, width=4, height=1))
    while flow.game.status is Status.RUNNING:
        flow.update(50)
    assert flow.game.status is Status.WON
    assert flow.phase is not Phase.SHAKING
    assert flow.menu is not None


# --- US3: entrada e saída da interface ---------------------------------------------------

from snake.flow import COUNTDOWN_MS, UI_ANIM_MS  # noqa: E402


def to_title(flow: Flow) -> Flow:
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.TITLE
    return flow


# T020
def test_new_flow_starts_with_title_entering_then_title():
    flow = Flow(seed=1)
    assert flow.phase is Phase.TITLE_IN
    flow.direction(Direction.UP)
    flow.confirm()  # ignorados durante a entrada
    flow.update(UI_ANIM_MS - 1)
    assert flow.phase is Phase.TITLE_IN
    flow.update(1)
    assert flow.phase is Phase.TITLE


def test_confirm_on_title_leaves_and_starts_countdown():
    flow = to_title(Flow(seed=1))
    flow.direction(Direction.UP)  # setas ignoradas na tela inicial
    assert flow.phase is Phase.TITLE
    flow.confirm()
    assert flow.phase is Phase.TITLE_OUT
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.COUNTDOWN


# T021
def test_countdown_shows_3_2_1_and_snake_waits():
    flow = to_title(Flow(seed=1))
    flow.confirm()
    flow.update(UI_ANIM_MS)
    start = flow.game.snake
    numbers = []
    for _ in range(int(COUNTDOWN_MS / 100) - 1):
        numbers.append(flow.countdown_number)
        flow.direction(Direction.UP)  # ignorado
        flow.confirm()  # ignorado
        flow.update(100)
    assert flow.phase is Phase.COUNTDOWN
    assert flow.game.snake == start
    assert flow.game.direction is Direction.RIGHT
    assert [n for i, n in enumerate(numbers) if i == 0 or numbers[i - 1] != n] == [3, 2, 1]
    flow.update(100)
    assert flow.phase is Phase.PLAYING
    assert flow.countdown_number is None


# T022
def test_end_menu_enters_then_accepts_input():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    while flow.phase in (Phase.PLAYING, Phase.SHAKING):
        flow.update(50)
    assert flow.phase is Phase.MENU_IN
    assert flow.menu is not None
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.MENU


def test_menu_key_during_entrance_completes_it_and_is_applied():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    while flow.phase in (Phase.PLAYING, Phase.SHAKING):
        flow.update(50)
    assert flow.phase is Phase.MENU_IN
    flow.direction(Direction.DOWN)
    assert flow.phase is Phase.MENU
    assert flow.menu.selected is MenuOption.OPTIONS  # 003/FR-016


def test_restart_leaves_menu_then_goes_to_countdown_not_title():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.confirm()
    assert flow.phase is Phase.MENU_OUT
    assert flow.game.status is Status.GAME_OVER  # ainda não reiniciou
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.COUNTDOWN
    assert flow.game.status is Status.RUNNING
    assert flow.menu is None


def test_quit_from_menu_is_immediate():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.direction(Direction.DOWN)
    flow.direction(Direction.DOWN)  # 003/FR-016
    flow.confirm()
    assert flow.quit_requested
    assert flow.phase is Phase.MENU


# T023
def test_ui_progress_by_phase():
    flow = Flow(seed=1)
    assert flow.ui_progress == 0  # TITLE_IN no início
    flow.update(UI_ANIM_MS / 2)
    mid_in = flow.ui_progress
    assert 0.5 < mid_in < 1  # ease-out: passa da metade na metade do tempo
    flow.update(UI_ANIM_MS / 2)
    assert flow.phase is Phase.TITLE and flow.ui_progress == 1
    flow.confirm()
    assert flow.ui_progress == 1  # TITLE_OUT começa cheio
    flow.update(UI_ANIM_MS / 2)
    assert 0 < flow.ui_progress < 1



# --- incremento pós-clarificação (FR-014, FR-015) ----------------------------------------

from snake.juice import COLLISION_SHAKE, EAT_SHAKE  # noqa: E402


# T032
def test_flow_uses_30x30_grid():
    flow = Flow(seed=1)
    assert (flow.game.width, flow.game.height) == (30, 30)
    assert flow.game.snake == ((15, 15), (14, 15), (13, 15))


# T031
def test_eating_starts_a_short_mini_shake():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    assert flow.game.score == 1
    assert not flow.shake.done
    assert 0 < flow.shake.amplitude <= EAT_SHAKE[0]
    flow.game.food = (0, 0)
    flow.update(EAT_SHAKE[1])
    assert flow.shake.done and flow.shake.offset == (0, 0)


def test_collision_right_after_eating_replaces_mini_shake():
    flow = to_playing(Flow(seed=1))
    flow.game._snake = [(28, 15), (27, 15), (26, 15)]
    flow.game.food = (29, 15)  # come na última coluna e bate no passo seguinte
    flow.update(STEP_MS)
    assert flow.game.score == 1
    flow.update(STEP_MS)
    assert flow.phase is Phase.SHAKING
    assert flow.shake.amplitude > EAT_SHAKE[0]
    flow.update(EAT_SHAKE[1] + 50)  # o mini tremor já teria acabado
    assert flow.phase is Phase.SHAKING and not flow.shake.done


# T037 (SC-003) — Restart até a cobra andar em no máximo 3,4 s
def test_restart_to_first_move_within_3_4_seconds():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.confirm()
    elapsed, head = 0, None
    while elapsed <= 5000:
        flow.update(10)
        elapsed += 10
        if head is None and flow.phase is Phase.COUNTDOWN:
            head = flow.game.snake[0]
        if head is not None and flow.game.snake[0] != head:
            break
    assert elapsed <= 3400


# --- 003: eventos sonoros ----------------------------------------------------------------

from snake.flow import SoundEvent  # noqa: E402

EXPECTED_SOUND_EVENTS = {
    "STEP", "EAT", "PULSE_POP", "CRASH", "COUNT", "GO", "NAV", "CONFIRM", "LOSE", "WIN",
    "VOLUME_PREVIEW", "MUSIC_TITLE", "MUSIC_GAME", "MUSIC_STOP", "MUSIC_DUCK", "MUSIC_UNDUCK",
    "TIMER_TICK", "TIMEOUT_ALARM", "MUSIC_FRENZY", "BOOM",  # 004
}


# T005
def test_sound_event_members():
    assert {e.name for e in SoundEvent} == EXPECTED_SOUND_EVENTS


def test_drain_sounds_returns_in_order_and_empties():
    flow = Flow(seed=1)
    flow._emit(SoundEvent.NAV)
    flow._emit(SoundEvent.CONFIRM)
    assert flow.drain_sounds()[-2:] == [SoundEvent.NAV, SoundEvent.CONFIRM]
    assert flow.drain_sounds() == []


# T009 — sons da jogabilidade
def playing_and_drained(seed: int = 1) -> Flow:
    flow = to_playing(Flow(seed=seed))
    flow.drain_sounds()
    return flow


def test_each_step_emits_step():
    flow = playing_and_drained()
    flow.game.food = (0, 0)
    flow.update(STEP_MS)
    assert flow.drain_sounds() == [SoundEvent.STEP]
    flow.update(STEP_MS - 1)
    assert flow.drain_sounds() == []


def test_eating_emits_eat_with_the_burst_then_pulse_pop_60ms_later():
    flow = playing_and_drained()
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    sounds = flow.drain_sounds()
    assert SoundEvent.EAT in sounds and len(flow.bursts) == 1
    assert SoundEvent.PULSE_POP not in sounds
    flow.game.food = (0, 0)
    flow.update(59)
    assert SoundEvent.PULSE_POP not in flow.drain_sounds()
    flow.update(1)
    assert SoundEvent.PULSE_POP in flow.drain_sounds()


def test_game_over_emits_crash_with_the_shake():
    flow = playing_and_drained()
    flow.game.food = (0, 0)
    events = []
    while flow.phase is Phase.PLAYING:
        flow.update(STEP_MS)
        events += flow.drain_sounds()
    assert flow.phase is Phase.SHAKING
    assert SoundEvent.CRASH in events
    assert SoundEvent.STEP not in events[events.index(SoundEvent.CRASH):]


def test_turning_emits_nothing():
    flow = playing_and_drained()
    flow.direction(Direction.UP)
    assert flow.drain_sounds() == []


# T014 — música
def sounds_until(flow: Flow, phase: Phase, dt: float = 50) -> list:
    events = flow.drain_sounds()
    for _ in range(2000):
        if flow.phase is phase:
            return events
        if flow.phase is Phase.TITLE:
            flow.confirm()
        flow.update(dt)
        events += flow.drain_sounds()
    raise AssertionError(f"não chegou em {phase}")


def test_title_music_starts_with_the_title():
    assert SoundEvent.MUSIC_TITLE in Flow(seed=1).drain_sounds()


def test_game_music_starts_when_countdown_ends():
    flow = Flow(seed=1)
    events = sounds_until(flow, Phase.COUNTDOWN)
    assert SoundEvent.MUSIC_GAME not in events
    events = sounds_until(flow, Phase.PLAYING)
    assert SoundEvent.MUSIC_GAME in events


def test_loss_stops_music_then_plays_lose_jingle():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    events = sounds_until(flow, Phase.MENU)
    assert SoundEvent.MUSIC_STOP in events and SoundEvent.LOSE in events
    assert events.index(SoundEvent.MUSIC_STOP) < events.index(SoundEvent.LOSE)
    assert SoundEvent.WIN not in events


def test_win_stops_music_then_plays_win_jingle():
    flow = advance_through_title(Flow(seed=1, width=4, height=1))
    events = sounds_until(flow, Phase.MENU)
    assert SoundEvent.MUSIC_STOP in events and SoundEvent.WIN in events
    assert events.index(SoundEvent.MUSIC_STOP) < events.index(SoundEvent.WIN)



# --- T020: pausa, Opções e menus novos (003 / US4) ----------------------------------------

from snake.settings import AudioSettings  # noqa: E402


def make_flow(tmp_path=None, **kwargs) -> Flow:
    path = None if tmp_path is None else tmp_path / "settings.json"
    return Flow(seed=1, settings_path=path, **kwargs)


def open_options_from(flow: Flow, steps_down: int) -> None:
    for _ in range(steps_down):
        flow.direction(Direction.DOWN)
    flow.confirm()
    assert flow.phase is Phase.OPTIONS_IN
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.OPTIONS


def leave_options(flow: Flow, via_escape: bool = True) -> None:
    if via_escape:
        flow.escape()
    else:
        flow.direction(Direction.DOWN)
        flow.direction(Direction.DOWN)
        flow.confirm()
    assert flow.phase is Phase.OPTIONS_OUT
    flow.update(UI_ANIM_MS)


def paused(flow: Flow) -> Flow:
    flow.escape()
    assert flow.phase is Phase.PAUSE_IN
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.PAUSE
    return flow


def test_title_shows_play_and_options_menu():
    flow = to_title(Flow(seed=1))
    assert flow.title_menu.options[0] is MenuOption.PLAY
    assert flow.title_menu.selected is MenuOption.PLAY
    flow.direction(Direction.DOWN)
    assert flow.title_menu.selected is MenuOption.OPTIONS


def test_options_from_title_changes_volume_saves_and_returns(tmp_path):
    flow = to_title(make_flow(tmp_path))
    open_options_from(flow, 1)
    assert flow.options_menu.selected is MenuOption.MUSIC
    flow.direction(Direction.RIGHT)
    assert flow.settings.music == 70
    flow.direction(Direction.DOWN)
    flow.direction(Direction.LEFT)
    assert flow.settings.sfx == 70
    leave_options(flow)
    assert flow.phase is Phase.TITLE
    saved = AudioSettings.load(tmp_path / "settings.json")
    assert (saved.music, saved.sfx) == (70, 70)


def test_flow_loads_saved_volumes(tmp_path):
    AudioSettings(music=20, sfx=40).save(tmp_path / "settings.json")
    flow = make_flow(tmp_path)
    assert (flow.settings.music, flow.settings.sfx) == (20, 40)


def test_options_back_item_returns_to_origin():
    flow = to_title(Flow(seed=1))
    open_options_from(flow, 1)
    leave_options(flow, via_escape=False)
    assert flow.phase is Phase.TITLE


def test_options_from_end_menu_returns_to_end_menu():
    flow = to_menu(to_playing(Flow(seed=1)))
    open_options_from(flow, 1)
    leave_options(flow)
    assert flow.phase is Phase.MENU
    assert flow.menu.selected is MenuOption.OPTIONS


def test_escape_pauses_and_freezes_everything():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)  # come: partículas, pulso e mini tremor ativos
    flow.drain_sounds()
    paused(flow)
    snapshot = (flow.game.snake, flow.game.score, flow.game.food,
                [(p.x, p.y, p.age_ms) for b in flow.bursts for p in b.particles],
                flow.pulse.scale, flow.shake.amplitude)
    for _ in range(40):
        flow.update(50)
    assert (flow.game.snake, flow.game.score, flow.game.food,
            [(p.x, p.y, p.age_ms) for b in flow.bursts for p in b.particles],
            flow.pulse.scale, flow.shake.amplitude) == snapshot
    assert flow.pause_menu.selected is MenuOption.CONTINUE


def test_pause_ducks_music_and_continue_unducks():
    flow = to_playing(Flow(seed=1))
    flow.drain_sounds()
    flow.escape()
    assert SoundEvent.MUSIC_DUCK in flow.drain_sounds()
    flow.update(UI_ANIM_MS)
    flow.confirm()  # Continuar
    assert SoundEvent.MUSIC_UNDUCK in flow.drain_sounds()


def test_continue_resumes_after_quick_countdown_from_same_point():
    flow = to_playing(Flow(seed=1))
    flow.game.food = (0, 0)
    flow.direction(Direction.UP)
    flow.update(STEP_MS)
    head, direction = flow.game.snake[0], flow.game.direction
    paused(flow)
    flow.confirm()
    assert flow.phase is Phase.PAUSE_OUT
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.RESUME
    numbers = []
    for _ in range(14):  # 1400 ms
        numbers.append(flow.resume_number)
        flow.direction(Direction.LEFT)  # ignorado
        flow.confirm()  # ignorado
        flow.escape()  # ignorado
        flow.update(100)
    assert flow.phase is Phase.RESUME
    assert flow.game.snake[0] == head and flow.game.direction is direction
    assert [n for i, n in enumerate(numbers) if i == 0 or numbers[i - 1] != n] == [3, 2, 1]
    flow.update(100)  # 1500 ms
    assert flow.phase is Phase.PLAYING
    assert flow.game.snake[0] == head  # sem passos acumulados
    flow.update(STEP_MS)
    assert flow.game.snake[0] == (head[0], head[1] - 1)  # segue na mesma direção


def test_escape_in_pause_also_continues():
    flow = paused(to_playing(Flow(seed=1)))
    flow.escape()
    assert flow.phase is Phase.PAUSE_OUT
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.RESUME


def test_options_from_pause_returns_to_pause():
    flow = paused(to_playing(Flow(seed=1)))
    open_options_from(flow, 1)
    leave_options(flow)
    assert flow.phase is Phase.PAUSE


def test_pause_to_title_abandons_game():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    assert flow.game.score == 1
    paused(flow)
    flow.drain_sounds()
    flow.direction(Direction.DOWN)
    flow.direction(Direction.DOWN)
    assert flow.pause_menu.selected is MenuOption.TITLE
    flow.confirm()
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.TITLE_IN
    assert flow.game.score == 0 and flow.game.snake == ((15, 15), (14, 15), (13, 15))
    events = flow.drain_sounds()
    assert SoundEvent.MUSIC_STOP in events and SoundEvent.MUSIC_TITLE in events


def test_escape_is_ignored_outside_playing_pause_and_options():
    flow = to_title(Flow(seed=1))
    flow.escape()
    assert flow.phase is Phase.TITLE
    flow.confirm()
    flow.update(UI_ANIM_MS)
    assert flow.phase is Phase.COUNTDOWN
    flow.escape()
    assert flow.phase is Phase.COUNTDOWN
    to_playing(flow)
    flow.game.food = (0, 0)
    while flow.phase is Phase.PLAYING:
        flow.update(STEP_MS)
    assert flow.phase is Phase.SHAKING
    flow.escape()
    assert flow.phase is Phase.SHAKING
    to_menu(flow)
    flow.escape()
    assert flow.phase is Phase.MENU


def test_pulse_pop_waits_while_paused():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    flow.drain_sounds()
    paused(flow)
    for _ in range(10):
        flow.update(50)
    assert SoundEvent.PULSE_POP not in flow.drain_sounds()


# T027 — sons de interface
def drain_while(flow: Flow, ms: float, dt: float = 50) -> list:
    events = []
    for _ in range(int(ms // dt)):
        flow.update(dt)
        events += flow.drain_sounds()
    return events


def test_countdown_beeps_on_each_number_then_go():
    flow = to_title(Flow(seed=1))
    flow.drain_sounds()
    flow.confirm()
    flow.drain_sounds()
    events = drain_while(flow, UI_ANIM_MS + COUNTDOWN_MS + 50)
    assert events.count(SoundEvent.COUNT) == 3
    assert events.count(SoundEvent.GO) == 1
    assert events.index(SoundEvent.GO) > max(i for i, e in enumerate(events) if e is SoundEvent.COUNT)


def test_resume_beeps_on_each_number_then_go():
    flow = paused(to_playing(Flow(seed=1)))
    flow.confirm()
    flow.drain_sounds()
    events = drain_while(flow, UI_ANIM_MS + 1500 + 50)
    assert events.count(SoundEvent.COUNT) == 3 and events.count(SoundEvent.GO) == 1


def test_nav_only_when_selection_changes():
    flow = to_title(Flow(seed=1))
    flow.drain_sounds()
    flow.direction(Direction.UP)  # já está no topo
    assert flow.drain_sounds() == []
    flow.direction(Direction.DOWN)
    assert flow.drain_sounds() == [SoundEvent.NAV]
    flow.direction(Direction.DOWN)  # já está na última
    assert flow.drain_sounds() == []


def test_confirm_sound_on_accepted_confirmations():
    flow = to_title(Flow(seed=1))
    flow.drain_sounds()
    flow.confirm()
    assert SoundEvent.CONFIRM in flow.drain_sounds()
    to_menu(to_playing(flow))
    flow.drain_sounds()
    flow.confirm()  # Restart
    assert SoundEvent.CONFIRM in flow.drain_sounds()


def test_quit_plays_confirm_sound():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.direction(Direction.DOWN)
    flow.direction(Direction.DOWN)
    flow.drain_sounds()
    flow.confirm()
    assert flow.quit_requested and SoundEvent.CONFIRM in flow.drain_sounds()


def test_volume_sliders_sound_only_when_value_changes():
    flow = to_title(Flow(seed=1, settings=AudioSettings(music=100, sfx=80)))
    open_options_from(flow, 1)
    flow.drain_sounds()
    flow.direction(Direction.RIGHT)  # música já em 100%
    assert flow.drain_sounds() == []
    flow.direction(Direction.LEFT)
    assert flow.drain_sounds() == [SoundEvent.NAV]
    flow.direction(Direction.DOWN)
    flow.drain_sounds()
    flow.direction(Direction.RIGHT)  # efeitos: toca a amostra
    assert flow.drain_sounds() == [SoundEvent.VOLUME_PREVIEW]


def test_ignored_keys_make_no_sound():
    flow = Flow(seed=1)  # TITLE_IN
    flow.drain_sounds()
    flow.direction(Direction.DOWN)
    flow.confirm()
    flow.escape()
    assert flow.drain_sounds() == []
    to_title(flow)
    flow.confirm()
    flow.update(UI_ANIM_MS)  # contagem
    flow.drain_sounds()
    flow.direction(Direction.UP)
    flow.confirm()
    flow.escape()
    assert flow.drain_sounds() == []


# --- 004: velocidade progressiva -------------------------------------------------------


def feed_once(flow: Flow) -> None:
    """Põe a fruta na frente da cabeça (a cobra anda para a direita) e dá um passo para comer."""
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(STEP_MS)
    flow.game.food = (0, 0)  # longe do caminho


# T006 — FR-002/FR-003
def test_step_interval_shrinks_after_growing():
    flow = to_playing(Flow(seed=1))
    feed_once(flow)
    assert len(flow.game.snake) == 4
    head = flow.game.snake[0]
    flow.update(123)
    assert flow.game.snake[0] == head
    flow.update(1)  # 124 ms
    assert flow.game.snake[0] == (head[0] + 1, head[1])


def test_several_steps_in_one_update_use_the_recalculated_interval():
    flow = to_playing(Flow(seed=1))
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    flow.update(125 + 124)  # come no 1º passo (125 ms); o 2º já usa 124 ms
    assert flow.game.snake[0] == (hx + 2, hy)


def test_restart_brings_back_the_initial_speed():
    flow = to_playing(Flow(seed=1))
    feed_once(flow)
    to_menu(flow)
    flow.confirm()  # Restart
    to_playing(flow)
    flow.game.food = (0, 0)
    head = flow.game.snake[0]
    flow.update(124)
    assert flow.game.snake[0] == head
    flow.update(1)
    assert flow.game.snake[0] == (head[0] + 1, head[1])


# --- 004: Feeding Frenzy (regras) ------------------------------------------------------


def eat_normal_in_front(flow: Flow) -> list:
    """Põe a fruta normal na frente da cabeça e avança até ela ser comida; devolve os sons."""
    hx, hy = flow.game.snake[0]
    flow.game.food = (hx + 1, hy)
    score = flow.game.score
    events = []
    while flow.game.score == score:
        flow.update(10)
        events += flow.drain_sounds()
    return events


def into_frenzy(flow: Flow | None = None, score: int = 9) -> tuple[Flow, list]:
    """Leva a partida ao limiar e avança até o Frenzy estar rodando (cobra andando)."""
    flow = flow or playing_and_drained()
    flow.game.score = score
    events = eat_normal_in_front(flow)
    assert flow.frenzy is not None
    for _ in range(1000):
        if flow.phase is Phase.PLAYING:
            break
        flow.update(10)
        events += flow.drain_sounds()
    assert flow.phase is Phase.PLAYING and flow.frenzy is not None
    return flow, events


def run_until_normal(flow: Flow) -> list:
    events = []
    for _ in range(1000):
        if flow.phase is Phase.PLAYING and flow.frenzy is None:
            return events
        flow.update(10)
        events += flow.drain_sounds()
    raise AssertionError(f"não voltou ao normal (fase {flow.phase})")


def specials_in_front(flow: Flow, count: int) -> None:
    hx, hy = flow.game.snake[0]
    flow.game.specials = {(hx + i, hy): i % 2 for i in range(1, count + 1)}


# T014 — FR-004
def test_frenzy_starts_exactly_at_the_thresholds():
    flow = playing_and_drained()
    flow.game.score = 10
    eat_normal_in_front(flow)  # 11: não é limiar
    assert flow.frenzy is None
    flow.game.score = 18
    eat_normal_in_front(flow)  # 19
    assert flow.frenzy is None
    flow, _ = into_frenzy(flow, score=9)  # 10
    assert flow.frenzy_count == 1
    specials_in_front(flow, 1)
    run_until_normal(flow)
    flow.game.score = 10
    eat_normal_in_front(flow)  # 11: o próximo é 20
    assert flow.frenzy is None
    flow.game.score = 19
    flow, _ = into_frenzy(flow, score=19)  # 20
    assert flow.frenzy_count == 2
    specials_in_front(flow, 1)
    run_until_normal(flow)
    flow.game.score = 29
    eat_normal_in_front(flow)  # 30: não é limiar (o próximo é 40)
    assert flow.frenzy is None


def test_frenzy_start_swaps_music_and_places_specials():
    flow, events = into_frenzy()
    assert events.index(SoundEvent.MUSIC_STOP) < events.index(SoundEvent.MUSIC_FRENZY)
    assert flow.game.in_frenzy and flow.game.food is None
    assert len(flow.game.specials) == 10
    assert flow.frenzy.seconds_left == 20
    assert flow.timer_visible


def test_frenzy_steps_use_the_bonus_interval():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    interval = 124 / 1.5  # comprimento 4
    head = flow.game.snake[0]
    flow.update(interval - 1)
    assert flow.game.snake[0] == head
    flow.update(1)
    assert flow.game.snake[0] == (head[0] + 1, head[1])


def test_eating_a_special_keeps_score_and_length_with_colored_particles():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    flow.update(70)  # sem passo ainda; o "pop" da fruta normal (60 ms) já passou
    flow.drain_sounds()
    specials_in_front(flow, 2)
    flow.game.specials[(0, 0)] = 0  # sobra uma para o modo não terminar
    score, length = flow.game.score, len(flow.game.snake)
    flow.bursts = []
    flow.update(124 / 1.5 - 70)
    events = flow.drain_sounds()
    assert SoundEvent.EAT in events and SoundEvent.PULSE_POP not in events
    assert (flow.game.score, len(flow.game.snake)) == (score, length)
    assert [b.tint for b in flow.bursts] == ["gold"]  # variante 1 → dourada
    flow.update(200)
    assert SoundEvent.PULSE_POP not in flow.drain_sounds()


def test_timer_only_runs_while_the_snake_moves():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    flow.update(50)
    assert flow.frenzy.remaining_ms == 20_000 - 50
    paused(flow)
    flow.update(5_000)
    flow.confirm()  # Continuar
    while flow.phase is not Phase.PLAYING:
        flow.update(50)
    assert flow.frenzy.remaining_ms == 20_000 - 50


def test_last_seconds_tick_and_pulse_the_timer():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    flow.frenzy.remaining_ms = 5_050
    flow.update(50)
    assert SoundEvent.TIMER_TICK in flow.drain_sounds()
    assert flow.timer_pulse.scale != 1 or flow.timer_pulse.flash > 0
    flow.update(500)
    assert SoundEvent.TIMER_TICK not in flow.drain_sounds()


def test_eating_the_last_special_returns_to_normal_with_the_same_length():
    flow, _ = into_frenzy()
    length = len(flow.game.snake)
    specials_in_front(flow, 1)
    events = run_until_normal(flow)
    assert SoundEvent.MUSIC_GAME in events
    assert not flow.game.in_frenzy and flow.game.food is not None
    assert len(flow.game.snake) == length
    assert not flow.timer_visible


def test_last_special_wins_over_time_running_out_in_the_same_frame():
    flow, _ = into_frenzy()
    specials_in_front(flow, 1)
    flow.frenzy.remaining_ms = 10
    flow.update(124 / 1.5)  # come a última e o tempo zera no mesmo quadro
    assert flow.game.status is Status.RUNNING
    assert flow.phase is not Phase.TIMEOUT
    run_until_normal(flow)


def test_time_running_out_is_a_game_over_with_its_own_signal():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    flow.update(200)  # o mini tremor da última fruta normal (150 ms) termina
    flow.frenzy.remaining_ms = 30
    flow.update(30)
    events = flow.drain_sounds()
    assert flow.phase is Phase.TIMEOUT
    assert flow.game.status is Status.GAME_OVER
    assert SoundEvent.MUSIC_STOP in events and SoundEvent.TIMEOUT_ALARM in events
    assert SoundEvent.CRASH not in events
    assert flow.shake.done
    assert flow.timer_visible and flow.frenzy.seconds_left == 0
    blinks = set()
    for _ in range(8):
        blinks.add(flow.timeout_blink)
        flow.update(150)
        if flow.phase is not Phase.TIMEOUT:
            break
    assert blinks == {True, False}


def test_timeout_leads_to_the_end_menu_with_lose_jingle():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    flow.frenzy.remaining_ms = 1
    flow.update(1)
    assert flow.phase is Phase.TIMEOUT
    flow.direction(Direction.UP)
    flow.confirm()
    flow.escape()
    assert flow.phase is Phase.TIMEOUT  # teclas ignoradas
    flow.drain_sounds()
    flow.update(1_199)
    assert flow.phase is Phase.TIMEOUT
    flow.update(1)
    assert flow.phase is Phase.MENU_IN
    assert SoundEvent.LOSE in flow.drain_sounds()
    assert flow.frenzy is None


def test_collision_during_frenzy_is_a_normal_game_over():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    events = []
    while flow.phase is Phase.PLAYING:
        flow.update(50)
        events += flow.drain_sounds()
    assert flow.phase is Phase.SHAKING
    assert SoundEvent.CRASH in events
    assert flow.frenzy is None


def test_restart_resets_the_frenzy_sequence():
    flow, _ = into_frenzy()
    flow.game.specials = {(0, 0): 0}
    to_menu(flow)
    flow.confirm()  # Restart
    to_playing(flow)
    assert flow.frenzy is None and flow.frenzy_count == 0
    assert not flow.game.in_frenzy
    flow, _ = into_frenzy(flow, score=9)  # o primeiro limiar volta a ser 10
    assert flow.frenzy_count == 1


def test_pause_to_title_resets_the_frenzy():
    flow, _ = into_frenzy()
    paused(flow)
    flow.direction(Direction.DOWN)
    flow.direction(Direction.DOWN)  # "Tela inicial"
    flow.confirm()
    while flow.phase is not Phase.TITLE:
        flow.update(50)
    assert flow.frenzy is None and flow.frenzy_count == 0
    assert not flow.game.in_frenzy


# --- 004: abertura "FEEDING FRENZY" ---------------------------------------------------


def at_intro() -> tuple[Flow, list]:
    flow = playing_and_drained()
    flow.game.score = 9
    events = eat_normal_in_front(flow)
    assert flow.phase is Phase.FRENZY_INTRO and flow.phase_ms == 0
    return flow, events


def tinted(flow: Flow, tint: str) -> int:
    return sum(1 for b in flow.bursts if b.tint == tint)


# T021 — FR-013/FR-014/FR-015
def test_threshold_opens_the_intro_with_everything_stopped():
    flow, events = at_intro()
    assert SoundEvent.MUSIC_STOP in events and SoundEvent.MUSIC_FRENZY not in events
    assert len(flow.game.specials) == 10
    head = flow.game.snake[0]
    flow.update(1_000)
    assert flow.game.snake[0] == head  # cobra parada
    assert flow.frenzy.remaining_ms == 20_000  # cronômetro parado
    assert not flow.timer_visible  # o cronômetro só aparece no fim da abertura


def test_stamps_fall_from_4x_to_1x_with_ease_in():
    flow, _ = at_intro()
    flow.update(199)
    assert flow.stamp_scales == (None, None)
    flow.update(1)  # 200 ms
    assert flow.stamp_scales == (4.0, None)
    flow.update(150)  # 350 ms: metade da queda com ease_in -> 4 - 3 * 0,25
    assert flow.stamp_scales[0] == 3.25
    flow.update(150)  # 500 ms
    assert flow.stamp_scales == (1.0, None)
    flow.update(299)  # 799 ms
    assert flow.stamp_scales == (1.0, None)
    flow.update(1)  # 800 ms
    assert flow.stamp_scales == (1.0, 4.0)
    flow.update(300)  # 1 100 ms
    assert flow.stamp_scales == (1.0, 1.0)


def test_each_impact_booms_shakes_and_spreads_debris():
    flow, _ = at_intro()
    flow.update(499)
    assert SoundEvent.BOOM not in flow.drain_sounds()
    assert tinted(flow, "purple") == 0
    flow.update(1)  # 500 ms: FEEDING bate
    assert flow.drain_sounds().count(SoundEvent.BOOM) == 1
    assert tinted(flow, "purple") == 5
    assert not flow.shake.done
    flow.update(599)
    assert SoundEvent.BOOM not in flow.drain_sounds()
    flow.update(1)  # 1 100 ms: FRENZY bate
    assert flow.drain_sounds().count(SoundEvent.BOOM) == 1
    assert tinted(flow, "gold") == 5
    assert not flow.shake.done


def test_stamps_fade_out_then_frenzy_music_and_timer_start():
    flow, _ = at_intro()
    flow.update(1_600)
    assert flow.stamp_alpha == 1.0
    flow.update(150)
    assert abs(flow.stamp_alpha - 0.5) < 1e-9
    flow.drain_sounds()
    flow.update(149)
    assert flow.phase is Phase.FRENZY_INTRO
    flow.update(1)  # 1 900 ms
    assert flow.phase is Phase.PLAYING
    assert SoundEvent.MUSIC_FRENZY in flow.drain_sounds()
    assert flow.frenzy.remaining_ms == 20_000
    flow.update(50)
    assert flow.frenzy.remaining_ms == 20_000 - 50


def test_keys_are_ignored_during_the_intro():
    flow, _ = at_intro()
    flow.drain_sounds()
    flow.escape()
    flow.confirm()
    flow.direction(Direction.UP)
    assert flow.phase is Phase.FRENZY_INTRO
    assert flow.drain_sounds() == []
    flow.update(1_900)
    assert flow.game.direction is Direction.RIGHT


def test_stamp_origins_are_on_a_diagonal_around_the_center():
    flow, _ = at_intro()
    (fx, fy), (zx, zy) = flow.stamp_origins
    cx, cy = flow.game.width / 2, flow.game.height / 2
    assert fx < cx < zx and fy < cy < zy


# --- 004: "SURVIVED!" -------------------------------------------------------------------


def survived_flow() -> tuple[Flow, list, int]:
    flow, _ = into_frenzy()
    length = len(flow.game.snake)
    specials_in_front(flow, 1)
    events = []
    while flow.phase is Phase.PLAYING:
        flow.update(10)
        events += flow.drain_sounds()
    return flow, events, length


# T025 — FR-017
def test_last_special_opens_survived_with_the_game_stopped():
    flow, events, length = survived_flow()
    assert flow.phase is Phase.SURVIVED
    assert SoundEvent.MUSIC_STOP in events
    assert not flow.game.in_frenzy and flow.game.food is not None
    assert len(flow.game.snake) == length
    assert not flow.timer_visible
    head = flow.game.snake[0]
    flow.update(1_000)
    assert flow.game.snake[0] == head


def test_survived_word_eases_in_holds_and_leaves():
    flow, _, _ = survived_flow()
    assert flow.survived_progress == 0
    flow.update(250)
    assert 0 < flow.survived_progress < 1
    flow.update(250)  # 500 ms
    assert flow.survived_progress == 1
    flow.update(500)  # 1 000 ms
    assert flow.survived_progress == 1
    flow.update(250)
    assert 0 < flow.survived_progress < 1
    flow.update(249)  # 1 499 ms
    assert flow.phase is Phase.SURVIVED


def test_survived_ends_back_in_normal_play_with_game_music():
    flow, _, length = survived_flow()
    flow.escape()
    flow.confirm()
    flow.direction(Direction.UP)
    assert flow.phase is Phase.SURVIVED  # teclas ignoradas
    flow.drain_sounds()
    flow.update(1_500)
    assert flow.phase is Phase.PLAYING
    assert SoundEvent.MUSIC_GAME in flow.drain_sounds()
    assert flow.game.direction is Direction.RIGHT
    head = flow.game.snake[0]
    flow.game.food = (0, 0)
    flow.update(124 - 1)  # velocidade normal para o comprimento 4
    assert flow.game.snake[0] == head
    flow.update(1)
    assert flow.game.snake[0] != head
