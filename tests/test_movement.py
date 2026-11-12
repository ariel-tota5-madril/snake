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


# T010 (atualizado pelo input buffer): o segundo comando vale no passo seguinte
def test_second_turn_is_buffered_for_the_next_step():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.UP)
    game.turn(Direction.LEFT)  # válido a partir de UP: fica guardado para o próximo passo
    game.step()
    assert game.direction is Direction.UP
    assert game.snake[0] == (10, 9)
    game.step()
    assert game.direction is Direction.LEFT
    assert game.snake[0] == (9, 9)


def test_quick_double_turn_never_reverses_onto_itself():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.DOWN)
    game.turn(Direction.LEFT)
    game.step()
    assert game.status is Status.RUNNING
    assert game.snake[0] == (10, 11)


# Input buffer: até 2 comandos guardados, validados contra o último da fila
def test_quick_u_turn_is_applied_over_two_steps():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.DOWN)
    game.turn(Direction.LEFT)  # meia-volta rápida: desce e depois vai para a esquerda
    game.step()
    game.step()
    assert game.snake[0] == (9, 11)
    assert game.status is Status.RUNNING


def test_buffer_holds_at_most_two_commands():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.UP)
    game.turn(Direction.LEFT)
    game.turn(Direction.DOWN)  # fila cheia: descartado
    game.step()
    game.step()
    game.step()
    assert game.direction is Direction.LEFT
    assert game.snake[0] == (8, 9)


def test_buffered_turn_is_checked_against_the_last_queued_direction():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.UP)
    game.turn(Direction.DOWN)  # oposto de UP (o último da fila): ignorado
    game.turn(Direction.UP)  # repetido: ignorado, não ocupa a fila
    game.turn(Direction.RIGHT)
    game.step()
    game.step()
    assert game.direction is Direction.RIGHT
    assert game.snake[0] == (11, 9)


def test_same_direction_as_current_is_not_queued():
    game = make_game()
    game.food = (0, 0)
    game.turn(Direction.RIGHT)  # já anda para a direita: não gasta espaço
    game.turn(Direction.UP)
    game.turn(Direction.LEFT)
    game.step()
    game.step()
    assert game.snake[0] == (9, 9)


def test_restart_clears_the_buffer():
    game = make_game()
    game.turn(Direction.UP)
    game.turn(Direction.LEFT)
    game.restart()
    game.food = (0, 0)
    game.step()
    assert game.direction is Direction.RIGHT
