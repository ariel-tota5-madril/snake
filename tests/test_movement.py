from snake.core import Direction, Game, Status


def make_game(**kwargs) -> Game:
    return Game(seed=1, **kwargs)


def test_initial_state():
    game = make_game()
    assert (game.width, game.height) == (20, 20)
    assert game.snake == ((10, 10), (9, 10), (8, 10))
    assert game.direction is Direction.RIGHT
    assert game.score == 0
    assert game.status is Status.RUNNING


# T008
def test_step_without_input_moves_one_cell_right_and_keeps_length():
    game = make_game()
    game.food = (0, 0)  # fora do caminho
    game.step()
    assert game.snake == ((11, 10), (10, 10), (9, 10))
    assert len(game.snake) == 3


# T009
def test_turn_up_then_step_moves_up():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.UP)
    game.step()
    assert game.snake[0] == (10, 9)
    assert game.direction is Direction.UP


def test_turn_to_opposite_direction_is_ignored():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.LEFT)
    game.step()
    assert game.direction is Direction.RIGHT
    assert game.snake[0] == (11, 10)


# T010
def test_only_first_valid_turn_per_step_is_applied():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.UP)
    game.turn(Direction.LEFT)  # válido a partir de UP, mas é o segundo do passo
    game.step()
    assert game.direction is Direction.UP
    assert game.snake[0] == (10, 9)


def test_quick_double_turn_never_reverses_onto_itself():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.DOWN)
    game.turn(Direction.LEFT)
    game.step()
    assert game.status is Status.RUNNING
    assert game.snake[0] == (10, 11)
