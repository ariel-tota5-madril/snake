import json

import pytest

from snake.settings import DEFAULT_MUSIC, DEFAULT_SFX, AudioSettings


# T018
def test_defaults_are_60_and_80():
    s = AudioSettings()
    assert (s.music, s.sfx) == (60, 80) == (DEFAULT_MUSIC, DEFAULT_SFX)


def test_adjust_moves_by_ten_and_reports_change():
    s = AudioSettings()
    assert s.adjust("music", +1) is True and s.music == 70
    assert s.adjust("sfx", -1) is True and s.sfx == 70


def test_adjust_is_clamped_to_0_and_100():
    s = AudioSettings(music=100, sfx=0)
    assert s.adjust("music", +1) is False and s.music == 100
    assert s.adjust("sfx", -1) is False and s.sfx == 0


def test_save_and_load_round_trip_creates_folder(tmp_path):
    path = tmp_path / "config" / "snake" / "settings.json"
    AudioSettings(music=30, sfx=100).save(path)
    loaded = AudioSettings.load(path)
    assert (loaded.music, loaded.sfx) == (30, 100)


@pytest.mark.parametrize("content", [
    None,  # arquivo ausente
    "isto não é json",
    json.dumps([1, 2]),
    json.dumps({"music": "alto", "sfx": 80}),
    json.dumps({"music": 150, "sfx": 80}),
    json.dumps({"music": -10, "sfx": 80}),
    json.dumps({"sfx": 80}),
])
def test_invalid_or_missing_file_loads_defaults(tmp_path, content):
    path = tmp_path / "settings.json"
    if content is not None:
        path.write_text(content)
    loaded = AudioSettings.load(path)
    assert (loaded.music, loaded.sfx) == (60, 80)


def test_loaded_values_snap_to_steps_of_ten(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"music": 47, "sfx": 83}))
    loaded = AudioSettings.load(path)
    assert (loaded.music, loaded.sfx) == (50, 80)
