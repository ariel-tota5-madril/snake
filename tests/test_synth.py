from array import array

import pytest

from snake.synth import RAMP_MS, SAMPLE_RATE, Note, mix, render

LIMIT = 32767
NEAR_ZERO = 1200  # ~3,7% da escala: início/fim de nota sem degrau audível


def samples_for(ms: float) -> int:
    return round(SAMPLE_RATE * ms / 1000)


# T003
def test_render_length_is_sum_of_note_durations():
    notes = [Note("square50", 440, 100), Note("triangle", 220, 50), Note("noise", 0, 30)]
    out = render(notes)
    assert isinstance(out, array) and out.typecode == "h"
    expected = sum(samples_for(n.ms) for n in notes)
    assert abs(len(out) - expected) <= len(notes)


@pytest.mark.parametrize("wave", ["square50", "square25", "square12", "triangle", "noise"])
def test_samples_stay_within_16_bit_range(wave):
    out = render([Note(wave, 880, 200, volume=1.0)])
    assert max(out) <= LIMIT and min(out) >= -LIMIT
    assert max(abs(s) for s in out) > 1000  # não é silêncio


@pytest.mark.parametrize("wave", ["square50", "square25", "triangle", "noise"])
def test_each_note_starts_and_ends_near_zero(wave):
    out = render([Note(wave, 523, 120)])
    assert abs(out[0]) <= NEAR_ZERO
    assert abs(out[-1]) <= NEAR_ZERO


def test_ramp_is_short():
    assert RAMP_MS <= 3


def test_zero_frequency_is_silence():
    out = render([Note("square50", 0, 50)])
    assert set(out) == {0}


def test_noise_is_deterministic():
    a = render([Note("noise", 0, 80)])
    b = render([Note("noise", 0, 80)])
    assert a == b


def zero_crossings(samples) -> int:
    return sum(1 for x, y in zip(samples, samples[1:]) if (x < 0) != (y < 0))


def test_freq_end_slides_pitch_up():
    out = render([Note("square50", 300, 400, freq_end=1200)])
    half = len(out) // 2
    assert zero_crossings(out[half:]) > zero_crossings(out[:half]) * 1.5


def test_mix_pads_shorter_track_and_clips():
    loud = array("h", [30000] * 100)
    short = array("h", [30000] * 40)
    out = mix(loud, short)
    assert len(out) == 100
    assert max(out) == LIMIT  # 60000 foi limitado
    assert out[60] == 30000  # depois do fim da faixa curta, só a longa
