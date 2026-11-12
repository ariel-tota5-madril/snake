import json

from snake.highscores import CAPACITY, Entry, Highscores


def table(*scores: int) -> Highscores:
    return Highscores([Entry(f"P{i}", s) for i, s in enumerate(scores)])


# 005 / T011 — FR-006/FR-008
def test_empty_table_ranks_first():
    hs = Highscores()
    assert hs.rank_for(0) == 0
    assert hs.insert("ANA", 5) == 0
    assert hs.entries == [Entry("ANA", 5)]


def test_insert_keeps_descending_order():
    hs = table(30, 20, 10)
    assert hs.insert("NEW", 25) == 1
    assert [e.score for e in hs.entries] == [30, 25, 20, 10]


def test_ties_put_the_newcomer_below():
    hs = table(30, 20, 10)
    assert hs.insert("NEW", 20) == 2
    assert [e.name for e in hs.entries] == ["P0", "P1", "NEW", "P2"]


def test_partial_table_accepts_anything_at_the_bottom():
    hs = table(30, 20)
    assert hs.insert("LOW", 0) == 2


def test_full_table_drops_the_tenth():
    hs = table(*range(100, 0, -10))  # 100..10, cheio
    assert len(hs.entries) == CAPACITY == 10
    assert hs.insert("NEW", 55) == 5
    assert len(hs.entries) == 10
    assert hs.entries[-1].score == 20  # o antigo 10º (10) saiu


def test_non_qualifying_score_leaves_the_table_unchanged():
    hs = table(*range(100, 0, -10))
    before = list(hs.entries)
    assert hs.rank_for(10) is None  # empate com o 10º não entra (fica abaixo)
    assert hs.insert("NEW", 5) is None
    assert hs.entries == before


def test_same_name_can_repeat():
    hs = Highscores()
    hs.insert("ANA", 5)
    hs.insert("ANA", 7)
    assert [e.name for e in hs.entries] == ["ANA", "ANA"]


# FR-007 / SC-005
def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "sub" / "highscores.json"
    hs = table(30, 20, 10)
    hs.save(path)
    assert Highscores.load(path).entries == hs.entries


def test_load_tolerates_missing_and_invalid_files(tmp_path):
    assert Highscores.load(tmp_path / "nada.json").entries == []
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert Highscores.load(bad).entries == []
    bad.write_text(json.dumps({"name": "x"}))
    assert Highscores.load(bad).entries == []


def test_load_drops_bad_entries_then_sorts_and_caps(tmp_path):
    path = tmp_path / "hs.json"
    good = [{"name": f"N{i}", "score": i} for i in range(12)]
    bad = [
        {"name": "", "score": 50},
        {"name": "X" * 11, "score": 50},
        {"name": 3, "score": 50},
        {"name": "B", "score": True},
        {"name": "C", "score": -1},
        {"name": "D", "score": 2.5},
        "lixo",
        {"score": 9},
    ]
    path.write_text(json.dumps(bad + good))
    hs = Highscores.load(path)
    assert [e.score for e in hs.entries] == list(range(11, 1, -1))
