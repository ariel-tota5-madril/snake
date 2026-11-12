from snake.core import Direction, Game, Status


def make_game(**kwargs) -> Game:
    game = Game(seed=1, **kwargs)
    game.food = (0, 0)  # longe da cobra para não interferir
    return game


# T011
def test_hitting_the_wall_ends_the_game_and_snake_stays_inside():
    game = make_game()
    for _ in range(9):  # cabeça vai de x=10 até x=19 (última coluna)
        game.step()
    assert game.snake[0] == (19, 10)
    assert game.status is Status.RUNNING
    game.step()  # sairia para x=20
    assert game.status is Status.GAME_OVER
    assert game.snake[0] == (19, 10)
    assert all(0 <= x < game.width and 0 <= y < game.height for x, y in game.snake)


# T012
def test_hitting_own_body_ends_the_game():
    game = make_game()
    game._snake = [(5, 5), (6, 5), (6, 6), (5, 6), (4, 6)]
    game.direction = Direction.UP
    game.turn(Direction.RIGHT)  # (6, 5) é corpo, não é a cauda
    game.step()
    assert game.status is Status.GAME_OVER


def test_moving_into_cell_the_tail_just_left_is_allowed():
    game = make_game()
    # cobra em "anel": a cabeça (5, 5) desce para (5, 6), que é a cauda atual
    game._snake = [(5, 5), (5, 4), (6, 4), (6, 5), (6, 6), (5, 6)]
    game.direction = Direction.DOWN
    game.step()  # a cauda sai de (5, 6) no mesmo passo em que a cabeça entra
    assert game.status is Status.RUNNING
    assert game.snake[0] == (5, 6)


# T013
def test_after_game_over_step_and_turn_change_nothing():
    game = make_game()
    for _ in range(10):
        game.step()
    assert game.status is Status.GAME_OVER
    before = (game.snake, game.direction, game.food, game.score, game.status)
    game.turn(Direction.UP)
    game.step()
    assert (game.snake, game.direction, game.food, game.score, game.status) == before
