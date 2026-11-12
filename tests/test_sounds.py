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
