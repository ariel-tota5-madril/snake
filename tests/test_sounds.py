import pytest

from snake import sounds
from snake.flow import SoundEvent
from snake.synth import SAMPLE_RATE


@pytest.fixture(scope="module", autouse=True)
def built():
    sounds.build()


def duration_ms(samples) -> float:
    return len(samples) * 1000 / SAMPLE_RATE


def zero_crossings(samples) -> int:
    return sum(1 for x, y in zip(samples, samples[1:]) if (x < 0) != (y < 0))


# T008
def test_gameplay_effects_exist():
    for event in (SoundEvent.STEP, SoundEvent.EAT, SoundEvent.PULSE_POP, SoundEvent.CRASH):
        samples, volume = sounds.SFX[event]
        assert len(samples) > 0
        assert 0 < volume <= 1


def test_step_is_quietest_and_short():
    step_volume = sounds.SFX[SoundEvent.STEP][1]
    others = [v for e, (_, v) in sounds.SFX.items() if e is not SoundEvent.STEP]
    assert others and step_volume < min(others)
    assert duration_ms(sounds.SFX[SoundEvent.STEP][0]) <= 30


def test_eat_rises_in_pitch():
    samples = sounds.SFX[SoundEvent.EAT][0]
    half = len(samples) // 2
    assert zero_crossings(samples[half:]) > zero_crossings(samples[:half])


def test_crash_lasts_about_350ms():
    assert 300 <= duration_ms(sounds.SFX[SoundEvent.CRASH][0]) <= 400


# T013 — músicas e jingles
NEAR_ZERO = 1200


@pytest.mark.parametrize("event,bpm", [(SoundEvent.MUSIC_TITLE, 120), (SoundEvent.MUSIC_GAME, 150)])
def test_music_lasts_whole_bars_and_loops_without_click(event, bpm):
    samples = sounds.MUSIC[event]
    bar_ms = 4 * 60000 / bpm
    bars = duration_ms(samples) / bar_ms
    assert round(bars) >= 4
    assert abs(bars - round(bars)) * bar_ms <= 20  # erro de arredondamento das notas
    assert abs(samples[0]) <= NEAR_ZERO and abs(samples[-1]) <= NEAR_ZERO  # emenda sem estalo


def test_jingles_exist_and_are_short():
    for event in (SoundEvent.LOSE, SoundEvent.WIN):
        assert 0 < duration_ms(sounds.JINGLES[event]) < 2000


# T026 — sons de interface
def dominant_crossings_per_ms(samples) -> float:
    return zero_crossings(samples) / duration_ms(samples)


def test_ui_effects_exist():
    for event in (SoundEvent.COUNT, SoundEvent.GO, SoundEvent.NAV, SoundEvent.CONFIRM,
                  SoundEvent.VOLUME_PREVIEW):
        samples, volume = sounds.SFX[event]
        assert len(samples) > 0 and 0 < volume <= 1


def test_go_is_higher_and_longer_than_count():
    count, go = sounds.SFX[SoundEvent.COUNT][0], sounds.SFX[SoundEvent.GO][0]
    assert duration_ms(go) > duration_ms(count)
    assert dominant_crossings_per_ms(go) > dominant_crossings_per_ms(count)


# 004 / T013 — sons do cronômetro e música do Frenzy
def test_frenzy_timer_sounds_exist():
    for event in (SoundEvent.TIMER_TICK, SoundEvent.TIMEOUT_ALARM):
        samples, volume = sounds.SFX[event]
        assert len(samples) > 0
        assert 0 < volume <= 1
    assert duration_ms(sounds.SFX[SoundEvent.TIMER_TICK][0]) <= 50
    assert 400 <= duration_ms(sounds.SFX[SoundEvent.TIMEOUT_ALARM][0]) <= 800


def test_frenzy_music_lasts_whole_bars_at_180_bpm_and_loops_without_click():
    samples = sounds.MUSIC[SoundEvent.MUSIC_FRENZY]
    bar_ms = 4 * 60000 / 180
    bars = duration_ms(samples) / bar_ms
    assert round(bars) >= 4
    assert abs(bars - round(bars)) * bar_ms <= 20
    assert abs(samples[0]) <= NEAR_ZERO and abs(samples[-1]) <= NEAR_ZERO


# 004 / T020 — boom do carimbo
def test_boom_is_long_loud_and_clean():
    samples, volume = sounds.SFX[SoundEvent.BOOM]
    assert 500 <= duration_ms(samples) <= 700
    assert volume > sounds.SFX[SoundEvent.EAT][1]
    assert abs(samples[0]) <= NEAR_ZERO and abs(samples[-1]) <= NEAR_ZERO


# 005 / T009 — blip de digitação
def test_name_type_blip_is_short_and_soft():
    samples, volume = sounds.SFX[SoundEvent.NAME_TYPE]
    assert duration_ms(samples) <= 40
    assert volume < sounds.SFX[SoundEvent.EAT][1]


# 005 / T024 — sons do placar
@pytest.mark.parametrize(
    "event,low,high",
    [
        (SoundEvent.ROCKET_IGNITE, 600, 800),
        (SoundEvent.ROCKET_LAUNCH, 350, 450),
        (SoundEvent.ROCKET_HIT, 100, 180),
        (SoundEvent.ROCKET_LAND, 150, 250),
    ],
)
def test_rocket_sounds(event, low, high):
    samples, volume = sounds.SFX[event]
    assert low <= duration_ms(samples) <= high
    assert 0 < volume <= 1
    assert abs(samples[0]) <= NEAR_ZERO and abs(samples[-1]) <= NEAR_ZERO


def test_first_place_fanfare_is_a_jingle():
    samples = sounds.JINGLES[SoundEvent.FIRST_PLACE]
    assert 800 <= duration_ms(samples) <= 2500
