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
    assert flow.game.snake == ((10, 10), (9, 10), (8, 10))
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

    bare = Game(seed=11)

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
