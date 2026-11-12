import random

from snake.core import Game, Status
from snake.frenzy import FRENZY_MS, Frenzy, threshold


# 004 / T011 — FR-004: 10, 20, 40, 80… (dobra a cada vez)
def test_thresholds_double_each_time():
    assert [threshold(n) for n in range(5)] == [10, 20, 40, 80, 160]


# T011 — cronômetro (FR-008, FR-019)
def test_timer_starts_full():
    timer = Frenzy()
    assert timer.remaining_ms == FRENZY_MS == 20_000
    assert timer.seconds_left == 20
    assert not timer.warning and not timer.expired


def test_timer_shows_ceiling_seconds_and_never_goes_negative():
    timer = Frenzy()
    timer.update(1)
    assert timer.seconds_left == 20
    timer.update(999)
    assert timer.seconds_left == 19
    timer.update(50_000)
    assert timer.remaining_ms == 0
    assert timer.seconds_left == 0
    assert timer.expired


def test_warning_only_in_the_last_five_seconds():
    timer = Frenzy()
    timer.update(14_999)  # 5,001 s → mostra 6
    assert not timer.warning
    timer.update(1)  # 5,000 s → mostra 5
    assert timer.warning
    timer.update(4_999)
    assert timer.seconds_left == 1 and timer.warning
    timer.update(1)
    assert not timer.warning and timer.expired


def test_update_returns_warning_seconds_that_just_started():
    timer = Frenzy()
    assert timer.update(14_950) == []  # 5,05 s → 6
    assert timer.update(50) == [5]
    assert timer.update(500) == []
    assert timer.update(500) == [4]
    assert timer.update(2_500) == [3, 2]  # um dt grande cruza dois segundos
    assert timer.update(10_000) == [1]  # o "0" não é segundo de aviso


# 004 / T012 — frutas especiais no núcleo
def game_with_seed(seed: int = 3) -> Game:
    return Game(width=30, height=30, rng=random.Random(seed))


def test_start_frenzy_replaces_food_with_ten_alternating_specials():
    game = game_with_seed()
    assert game.start_frenzy() == 10
    assert game.in_frenzy
    assert game.food is None
    assert len(game.specials) == 10
    assert not set(game.specials) & set(game.snake)
    assert sorted(game.specials.values()) == [0] * 5 + [1] * 5


def test_specials_are_reproducible_with_the_same_seed():
    a, b = game_with_seed(9), game_with_seed(9)
    a.start_frenzy()
    b.start_frenzy()
    assert a.specials == b.specials


def test_fewer_specials_when_free_cells_are_scarce():
    game = Game(width=6, height=1, rng=random.Random(1))  # cobra ocupa 3 de 6 casas
    assert game.start_frenzy() == 3
    assert len(game.specials) == 3
    full = Game(width=4, height=1, rng=random.Random(1))
    full.step()  # come a única fruta: tabuleiro cheio
    assert full.start_frenzy() == 0
    assert not full.in_frenzy and full.specials == {}


def test_eating_a_special_removes_it_without_growth_or_score():
    game = game_with_seed()
    game.start_frenzy()
    hx, hy = game.snake[0]
    game.specials = {(hx + 1, hy): 0, (hx + 2, hy): 1}
    length, score = len(game.snake), game.score
    game.step()
    assert (hx + 1, hy) not in game.specials
    assert len(game.specials) == 1
    assert (len(game.snake), game.score) == (length, score)
    assert game.status is Status.RUNNING


def test_end_frenzy_brings_back_food_with_the_same_length():
    game = game_with_seed()
    length = len(game.snake)
    game.start_frenzy()
    for _ in range(3):
        game.step()
    game.end_frenzy()
    assert not game.in_frenzy
    assert game.specials == {}
    assert game.food is not None and game.food not in game.snake
    assert len(game.snake) == length


def test_fail_ends_the_game():
    game = game_with_seed()
    game.start_frenzy()
    game.fail()
    assert game.status is Status.GAME_OVER


def test_restart_clears_specials():
    game = game_with_seed()
    game.start_frenzy()
    game.restart()
    assert not game.in_frenzy
    assert game.specials == {}
    assert game.food is not None
