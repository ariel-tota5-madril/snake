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
