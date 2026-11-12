import random

from snake.core import Direction, Game, Status


def game(**kwargs) -> Game:
    return Game(width=20, height=20, rng=random.Random(1), **kwargs)  # cabeça (10, 10) para a direita


# 006 / T003 — FR-002, FR-003
def test_food_within_reach_is_eaten():
    for distance in (1, 2, 3):
        g = game()
        g.food = (10 + distance, 10)
        shot = g.tongue(3)
        assert shot.ate and shot.reach == distance and shot.target == (10 + distance, 10)
        assert g.score == 1
        assert g.food is not None and g.food not in g.snake and g.food != (10 + distance, 10)


def test_food_beyond_reach_is_not_eaten():
    g = game()
    g.food = (14, 10)
    shot = g.tongue(3)
    assert not shot.ate and shot.reach == 3 and shot.target is None
    assert g.score == 0 and g.food == (14, 10)


def test_wall_stops_the_tongue():
    g = Game(width=12, height=20, rng=random.Random(1))  # cabeça em (6, 10)
    g.food = (0, 0)
    for _ in range(4):
        g.step()  # cabeça em (10, 10): só a casa 11 antes da parede
    shot = g.tongue(3)
    assert shot.reach == 1 and not shot.ate


def test_body_blocks_the_tongue():
    g = game()
    # cobra em U: cabeça (10, 10) para a direita, corpo dobrando à frente em (11, 10)
    g._snake = [(10, 10), (10, 11), (11, 11), (11, 10), (12, 10)]
    g.direction = Direction.RIGHT
    g.food = (13, 10)
    shot = g.tongue(3)
    assert shot.reach == 0 and not shot.ate


def test_uses_the_current_direction_even_with_a_turn_queued():
    g = game()
    g.food = (12, 10)
    g.turn(Direction.UP)  # ainda não aplicado
    shot = g.tongue(3)
    assert shot.direction is Direction.RIGHT and shot.ate


def test_eating_with_the_tongue_grows_on_the_next_step():
    g = game()
    g.food = (12, 10)
    g.tongue(3)
    g.food = (0, 0)
    g.step()
    assert len(g.snake) == 4
    g.step()
    assert len(g.snake) == 4


def test_eating_the_last_free_cell_wins():
    g = Game(width=4, height=1, rng=random.Random(1))  # cobra (2,0)(1,0)(0,0); fruta em (3,0)
    shot = g.tongue(3)
    assert shot.ate and g.status is Status.WON


def test_no_tongue_when_the_game_is_over():
    g = game()
    g.status = Status.GAME_OVER
    g.food = (11, 10)
    shot = g.tongue(3)
    assert shot.reach == 0 and not shot.ate and g.score == 0


# --- 006 / T005 — recarga e animação (FR-004, FR-006, FR-013) -----------------------------

from snake.core import TongueShot  # noqa: E402
from snake.tongue import ANIM_MS, COOLDOWN_MS, Tongue  # noqa: E402

SHOT = TongueShot(Direction.RIGHT, 2, True, (12, 10))


def test_tongue_starts_ready():
    t = Tongue()
    assert t.ready and t.progress == 1 and t.extension == 0 and t.shot is None


def test_fire_starts_the_full_cooldown():
    t = Tongue()
    t.fire(SHOT)
    assert COOLDOWN_MS == 8000
    assert t.remaining_ms == 8000 and not t.ready and t.progress == 0
    assert t.shot == SHOT


def test_update_cooldown_reports_ready_once_and_stops_at_zero():
    t = Tongue()
    t.fire(SHOT)
    assert t.update_cooldown(4000) is False
    assert t.progress == 0.5
    assert t.update_cooldown(3999) is False
    assert t.update_cooldown(10) is True
    assert t.remaining_ms == 0 and t.ready
    assert t.update_cooldown(1000) is False


def test_extension_goes_out_and_back_in_300ms():
    t = Tongue()
    t.fire(SHOT)
    assert ANIM_MS == 300
    t.update_anim(75)
    assert 0 < t.extension < 1
    t.update_anim(75)
    assert t.extension == 1 and not t.retracting
    t.update_anim(75)
    assert 0 < t.extension < 1 and t.retracting
    t.update_anim(75)
    assert t.extension == 0
    t.update_anim(500)
    assert t.extension == 0
