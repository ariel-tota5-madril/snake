from snake.core import Direction, Game, Status


def lose(game: Game) -> None:
    game.food = (0, 0)
    while game.status is Status.RUNNING:
        game.step()


# T030
def test_restart_after_game_over_returns_to_initial_state():
    game = Game(seed=5)
    hx, hy = game.snake[0]
    game.food = (hx + 1, hy)
    game.step()  # come: score 1, cobra com 4 casas
    lose(game)
    assert game.status is Status.GAME_OVER

    game.restart()
    assert game.snake == ((10, 10), (9, 10), (8, 10))
    assert game.direction is Direction.RIGHT
    assert game.score == 0
    assert game.status is Status.RUNNING
    assert game.food is not None and game.food not in game.snake


# T031
def test_restart_after_win():
    # grade 4x1: cobra inicial ocupa (2,0), (1,0), (0,0); a única casa livre é (3,0)
    game = Game(width=4, height=1, seed=1)
    assert game.food == (3, 0)
    game.step()  # come a última comida possível
    assert game.status is Status.WON

    game.restart()
    assert game.status is Status.RUNNING
    assert game.snake == ((2, 0), (1, 0), (0, 0))
    assert game.score == 0
    assert game.food == (3, 0)


def test_same_seed_session_with_restart_is_reproducible():
    def session(seed: int) -> list:
        game = Game(seed=seed)
        foods = [game.food]
        lose(game)
        game.restart()
        foods.append(game.food)
        game.restart()
        foods.append(game.food)
        return foods

    assert session(9) == session(9)
