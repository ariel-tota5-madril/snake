from snake.core import Game


# T024
def test_score_starts_at_zero_and_counts_each_food():
    game = Game(seed=3)
    assert game.score == 0

    game.food = (0, 0)  # longe: anda sem comer
    game.step()
    game.step()
    assert game.score == 0

    for expected in (1, 2):
        hx, hy = game.snake[0]
        game.food = (hx + 1, hy)  # comida logo à frente
        game.step()
        assert game.score == expected
