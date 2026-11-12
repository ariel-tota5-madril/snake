import random

from snake.highscores import Entry, Highscores
from snake.scoreboard import VISIBLE_ROWS, Scoreboard


def board_for(scores: list[int], new_score: int, name: str = "YOU", seed: int = 1) -> Scoreboard:
    hs = Highscores([Entry(f"P{i}", s) for i, s in enumerate(scores)])
    before = list(hs.entries)
    rank = hs.insert(name, new_score)
    return Scoreboard(before, list(hs.entries), rank, Entry(name, new_score), random.Random(seed))


def finish(board: Scoreboard) -> Scoreboard:
    for _ in range(1000):
        if board.done:
            return board
        board.update(50)
    raise AssertionError("animação não terminou")


# 005 / T012 — placar estático (FR-006, FR-008, FR-009)
def test_five_visible_rows():
    assert VISIBLE_ROWS == 5


def test_non_qualifying_score_is_shown_outside_without_animation():
    scores = list(range(100, 0, -10))
    board = board_for(scores, 5)
    assert board.done
    assert board.outside == Entry("YOU", 5)
    assert board.view_top == len(scores) - VISIBLE_ROWS  # aberto no fim da lista
    assert all(not row.is_player for row in board.rows())


def test_rows_list_every_entry_at_its_line():
    board = finish(board_for([30, 20, 10], 25))
    rows = sorted(board.rows(), key=lambda r: r.y)
    assert [(r.y, r.entry.score) for r in rows] == [(0, 30), (1, 25), (2, 20), (3, 10)]
    assert [r.is_player for r in rows] == [False, True, False, False]
    assert board.outside is None


def test_scroll_moves_one_line_within_limits():
    board = finish(board_for([90, 80, 70, 60, 50, 40, 30, 20], 95))  # 9 linhas
    board.view_top = 0
    assert board.scroll(-1) is False
    assert board.scroll(1) is True and board.view_top == 1
    for _ in range(10):
        board.scroll(1)
    assert board.view_top == 9 - VISIBLE_ROWS
    assert board.scroll(1) is False


def test_short_table_does_not_scroll():
    board = finish(board_for([30], 10))
    assert board.view_top == 0
    assert board.scroll(1) is False


# --- 005 / T018 — explosão das letras (FR-013, FR-013a) ---------------------------------

from snake.scoreboard import (  # noqa: E402
    ACCEL_DIST,
    FOLLOW_AT,
    IGNITION_MS,
    REFORM_MS,
    SCATTER_MS,
    V_MAX,
    ScorePhase,
    Shatter,
)

ENTRY = Entry("BOB", 70)  # 5 caracteres: B, O, B, 7, 0


def test_shatter_scatters_then_reforms_one_line_below():
    sh = Shatter(ENTRY, 3.0, 4.0, random.Random(1))
    assert len(sh.offsets()) == 5
    assert all(o == (0, 0) for o in sh.offsets())
    sh.update(SCATTER_MS)
    assert max(abs(dx) + abs(dy) for dx, dy in sh.offsets()) > 0.5
    assert sh.base_y == 3.0
    sh.update(REFORM_MS / 2)
    assert 3.0 < sh.base_y < 4.0
    sh.update(REFORM_MS / 2)
    assert sh.done
    assert sh.base_y == 4.0
    assert all(abs(dx) < 1e-9 and abs(dy) < 1e-9 for dx, dy in sh.offsets())


def test_expelled_shatter_falls_and_fades():
    sh = Shatter(ENTRY, 9.0, None, random.Random(1))
    sh.update(400)
    mid = [dy for _, dy in sh.offsets()]
    sh.update(300)
    late = [dy for _, dy in sh.offsets()]
    assert sum(late) > sum(mid)  # gravidade puxa para baixo
    assert 0 < sh.alpha < 1
    sh.update(100)
    assert sh.done


def test_shatter_is_deterministic():
    a, b = Shatter(ENTRY, 1.0, 2.0, random.Random(4)), Shatter(ENTRY, 1.0, 2.0, random.Random(4))
    a.update(200)
    b.update(200)
    assert a.offsets() == b.offsets()


# --- 005 / T019 — foguete, câmera e impactos (FR-012 a FR-016, SC-003) ----------------------

FULL = list(range(100, 0, -10))  # 10 entradas: 100..10


def run(board: Scoreboard, ms: float, dt: float = 10) -> list:
    events = []
    t = 0.0
    while t < ms:
        board.update(dt)
        events += board.drain_events()
        t += dt
    return events


def test_ignition_on_the_ground_with_jitter_flame_and_expelled_tenth():
    board = board_for(FULL, 55)  # entra na posição 5
    assert not board.done and board.phase is ScorePhase.IGNITION
    events = run(board, 100)
    assert events[:2] == ["ignite", "hit"]  # o antigo 10º explode na ignição
    assert board.rocket_y == 9.0  # chão da lista
    assert board.rocket_offset != (0, 0)
    assert board.bursts and all(b.tint == "flame" for b in board.bursts)
    assert any(sh.to_y is None for sh in board.shatters)


def test_launch_accelerates_to_max_speed_and_keeps_it():
    board = board_for(FULL, 105)  # vai ao 1º: subida de 9 linhas
    events = run(board, IGNITION_MS + 10)
    assert "launch" in events and board.phase is ScorePhase.CLIMB
    t_acc = V_MAX / (V_MAX**2 / (2 * ACCEL_DIST))  # 0,6 s
    run(board, t_acc * 1000 + 100)
    y1 = board.rocket_y
    run(board, 200)
    y2 = board.rocket_y
    assert abs((y1 - y2) / 0.2 - V_MAX) < 0.3  # velocidade máxima constante


def test_camera_follows_above_the_middle_then_stops_at_the_top():
    board = board_for(FULL, 105)
    view0 = board.view_top
    assert view0 == 10 - VISIBLE_ROWS
    screen = []
    while board.phase in (ScorePhase.IGNITION, ScorePhase.CLIMB):
        board.update(10)
        screen.append((board.rocket_y - board.view_top, board.view_top))
    following = [s for s, v in screen if 0 < v < view0]
    assert following and all(abs(s - FOLLOW_AT) < 1e-6 for s in following)  # parado na tela
    after_top = [s for s, v in screen if v == 0]
    assert after_top[-1] < FOLLOW_AT  # volta a subir na tela com a câmera parada
    assert board.view_top == 0


def test_each_passed_entry_is_hit_and_reforms_one_line_below():
    board = board_for([90, 80, 70, 60], 85)  # não cheio: começa na linha 4, entra na 1
    events = run(board, 4000)
    assert events.count("hit") == 3  # passou por 80, 70 e 60
    assert "land" in events
    rows = sorted(board.rows(), key=lambda r: r.y)
    assert [(r.y, r.entry.score) for r in rows] == [(0, 90), (1, 85), (2, 80), (3, 70), (4, 60)]


def test_first_place_shows_after_landing():
    board = board_for([50, 40], 60)
    events = run(board, 5000)
    assert events.index("land") < events.index("first")
    assert board.first_place == 1
    assert board.done


def test_not_first_has_no_first_place():
    board = board_for([90, 40], 60)
    events = run(board, 5000)
    assert "first" not in events and board.first_place == 0
    assert board.done


def test_no_climb_when_entering_at_the_bottom():
    board = board_for([90, 80], 10)
    events = run(board, 3000)
    assert "launch" not in events and "hit" not in events
    assert events[0] == "ignite" and "land" in events


def test_worst_case_animation_fits_in_five_seconds():
    board = board_for(FULL, 105)
    elapsed = 0
    while not board.done:
        board.update(10)
        elapsed += 10
    assert elapsed <= 5000


def test_skip_reaches_the_same_final_state_without_events():
    played, skipped = board_for(FULL, 105, seed=3), board_for(FULL, 105, seed=3)
    run(played, 6000)
    run(skipped, 1200)
    skipped.drain_events()
    skipped.skip()
    assert skipped.done and skipped.drain_events() == []
    snap = lambda b: (sorted((r.y, r.entry) for r in b.rows()), b.view_top, b.first_place, b.rocket_y)
    assert snap(skipped) == snap(played)
    assert skipped.shatters == []


def test_scroll_only_after_the_animation():
    board = board_for(FULL, 55)
    assert board.scroll(-1) is False
    run(board, 6000)
    assert board.scroll(-1) is True


def test_same_seed_same_animation():
    a, b = board_for(FULL, 55, seed=8), board_for(FULL, 55, seed=8)
    run(a, 1500)
    run(b, 1500)
    assert a.rocket_offset == b.rocket_offset
    assert [s.offsets() for s in a.shatters] == [s.offsets() for s in b.shatters]
