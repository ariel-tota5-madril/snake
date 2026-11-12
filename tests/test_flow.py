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


def test_win_leads_to_menu():
    flow = to_playing(Flow(seed=1, width=4, height=1))
    assert flow.game.food == (3, 0)
    for _ in range(1000):
        if flow.phase is Phase.MENU:
            break
        flow.update(50)
    assert flow.game.status is Status.WON
    assert flow.menu is not None


def test_menu_selection_moves_with_up_and_down():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.direction(Direction.DOWN)
    assert flow.menu.selected is MenuOption.QUIT
    flow.direction(Direction.UP)
    assert flow.menu.selected is MenuOption.RESTART


def test_restart_starts_a_new_game():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.confirm()
    to_playing(flow)
    assert flow.game.status is Status.RUNNING
    assert flow.game.snake == ((15, 15), (14, 15), (13, 15))
    assert flow.game.score == 0
    assert flow.menu is None


def test_quit_option_requests_quit():
    flow = to_menu(to_playing(Flow(seed=1)))
    flow.direction(Direction.DOWN)
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
    flow = to_playing(Flow(seed=1, width=4, height=1))
    flow.update(STEP_MS)
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
    assert flow.menu.selected is MenuOption.QUIT


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
