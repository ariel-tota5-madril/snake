from snake.core import Direction, Game, Status


def in_grid(game: Game, cell) -> bool:
    x, y = cell
    return 0 <= x < game.width and 0 <= y < game.height


# T017
def test_new_game_has_one_food_inside_grid_and_off_the_snake():
    game = Game(seed=7)
    assert game.food is not None
    assert in_grid(game, game.food)
    assert game.food not in game.snake


# T018
def test_eating_grows_snake_and_spawns_new_food_on_free_cell():
    game = Game(seed=7)
    game.food = (11, 10)  # logo à frente da cabeça
    game.step()
    assert game.snake == ((11, 10), (10, 10), (9, 10), (8, 10))
    assert game.food is not None
    assert game.food != (11, 10)
    assert in_grid(game, game.food)
    assert game.food not in game.snake


# T019
def test_same_seed_and_commands_give_same_food_sequence():
    def play(seed: int) -> list:
        """Joga 200 passos perseguindo a comida; o piloto é determinístico."""
        game = Game(seed=seed)
        foods = [game.food]
        for _ in range(200):
            if game.status is not Status.RUNNING:
                break
            hx, hy = game.snake[0]
            fx, fy = game.food
            if fx != hx:
                game.turn(Direction.RIGHT if fx > hx else Direction.LEFT)
            game.turn(Direction.DOWN if fy > hy else Direction.UP)
            game.step()
            foods.append(game.food)
        return foods

    first, second = play(42), play(42)
    assert first == second
    assert len(set(f for f in first if f is not None)) > 1  # comeu ao menos uma vez


# T020 (FR-012)
def test_no_free_cell_after_eating_means_win():
    game = Game(width=2, height=2, seed=1)
    # grade 2x2: cobra ocupa 3 casas, comida na última livre
    game._snake = [(0, 1), (0, 0), (1, 0)]
    game.direction = Direction.RIGHT
    game.food = (1, 1)
    game.step()
    assert game.status is Status.WON
    assert game.food is None
    assert len(game.snake) == 4
