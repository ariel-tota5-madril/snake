import random

import pytest

from snake.juice import (
    COLLISION_SHAKE,
    EAT_SHAKE,
    ParticleBurst,
    ScorePulse,
    ScreenShake,
    ease_in,
    ease_out,
)


# T008
def test_ease_out_endpoints_monotonic_and_clamped():
    assert ease_out(0) == 0
    assert ease_out(1) == 1
    samples = [ease_out(i / 10) for i in range(11)]
    assert samples == sorted(samples)
    assert ease_out(-1) == 0
    assert ease_out(2) == 1


# T009
def test_particle_burst_starts_at_origin_and_dies_within_600ms():
    burst = ParticleBurst((100.0, 50.0), random.Random(1))
    assert len(burst.particles) == 16
    assert all((p.x, p.y) == (100.0, 50.0) for p in burst.particles)
    burst.update(300)
    assert not burst.done
    assert any((p.x, p.y) != (100.0, 50.0) for p in burst.particles)
    burst.update(300)
    assert burst.done
    assert burst.particles == []


def test_particle_bursts_are_deterministic_for_equal_seeds():
    a = ParticleBurst((0.0, 0.0), random.Random(7))
    b = ParticleBurst((0.0, 0.0), random.Random(7))
    a.update(100)
    b.update(100)
    assert [(p.x, p.y, p.life) for p in a.particles] == [(p.x, p.y, p.life) for p in b.particles]


# T010
def test_score_pulse_grows_flashes_and_returns_to_normal():
    pulse = ScorePulse()
    assert (pulse.scale, pulse.flash) == (1, 0)
    pulse.trigger()
    pulse.update(150)
    assert pulse.scale > 1
    assert 0 < pulse.flash < 1
    pulse.update(150)
    assert (pulse.scale, pulse.flash) == (1, 0)


def test_score_pulse_restarts_when_triggered_mid_pulse():
    pulse = ScorePulse()
    pulse.trigger()
    pulse.update(250)
    pulse.trigger()
    pulse.update(100)
    assert pulse.scale > 1  # se não reiniciasse, já teria terminado (350 ms > 300 ms)


# T015 / T030 — tremor configurável, em casas
def test_screen_shake_stays_within_decaying_amplitude_and_ends_at_origin():
    shake = ScreenShake(random.Random(3))
    assert shake.offset == (0, 0)
    amplitude, duration = COLLISION_SHAKE
    shake.trigger(amplitude, duration)
    amplitudes = []
    for _ in range(7):  # 7 x 50 ms = 350 ms
        shake.update(50)
        dx, dy = shake.offset
        limit = shake.amplitude
        amplitudes.append(limit)
        assert abs(dx) <= limit and abs(dy) <= limit
        assert not shake.done
    assert amplitudes == sorted(amplitudes, reverse=True)
    assert amplitudes[0] <= amplitude
    shake.update(50)  # 400 ms
    assert shake.done
    assert shake.offset == (0, 0)


def test_screen_shake_is_deterministic_for_equal_seeds():
    a, b = ScreenShake(random.Random(9)), ScreenShake(random.Random(9))
    a.trigger(*COLLISION_SHAKE)
    b.trigger(*COLLISION_SHAKE)
    offsets = []
    for _ in range(5):
        a.update(40)
        b.update(40)
        offsets.append((a.offset, b.offset))
    assert all(x == y for x, y in offsets)


def test_eat_shake_is_a_third_of_collision_and_lasts_150ms():
    assert EAT_SHAKE[0] == pytest.approx(COLLISION_SHAKE[0] / 3)
    assert EAT_SHAKE[1] == 150
    shake = ScreenShake(random.Random(1))
    shake.trigger(*EAT_SHAKE)
    shake.update(149)
    assert not shake.done
    shake.update(1)
    assert shake.done and shake.offset == (0, 0)


def test_new_trigger_replaces_running_shake():
    shake = ScreenShake(random.Random(1))
    shake.trigger(*EAT_SHAKE)
    shake.update(100)
    shake.trigger(*COLLISION_SHAKE)
    shake.update(100)  # 200 ms no total; o tremor de comer já teria acabado
    assert not shake.done
    assert shake.amplitude > EAT_SHAKE[0]


# T029 — pulso "punchy"
def test_score_pulse_punchy_curve():
    pulse = ScorePulse()
    pulse.trigger()
    assert pulse.warmth == 0  # começa branco
    pulse.update(60)
    assert pulse.scale == pytest.approx(1.8)
    assert pulse.warmth == 1  # já amarelo
    pulse.update(120)  # 180 ms
    assert pulse.scale == pytest.approx(0.9)
    pulse.update(60)  # 240 ms
    assert 0.9 < pulse.scale < 1
    pulse.update(60)  # 300 ms
    assert (pulse.scale, pulse.flash, pulse.warmth) == (1, 0, 0)


def test_score_pulse_minimum_is_the_dip():
    pulse = ScorePulse()
    pulse.trigger()
    scales = []
    for _ in range(29):
        pulse.update(10)
        scales.append(pulse.scale)
    assert max(scales) == pytest.approx(1.8)
    assert min(scales) == pytest.approx(0.9)


# 004 / T003 — ease_in para o carimbo e explosões configuráveis (detritos, partículas coloridas)
def test_ease_in_is_quadratic_and_clamped():
    assert ease_in(0) == 0
    assert ease_in(0.5) == 0.25
    assert ease_in(1) == 1
    assert ease_in(-1) == 0
    assert ease_in(2) == 1


def test_particle_burst_accepts_count_speed_life_and_tint():
    burst = ParticleBurst((5.0, 5.0), random.Random(2), count=12, speed=(6, 14), life_ms=900, tint="purple")
    assert len(burst.particles) == 12
    assert burst.tint == "purple"
    for p in burst.particles:
        assert 6 - 1e-9 <= (p.vx**2 + p.vy**2) ** 0.5 <= 14 + 1e-9
    burst.update(800)
    assert not burst.done
    assert all(0 < p.life < 1 for p in burst.particles)
    burst.update(100)
    assert burst.done


def test_particle_burst_defaults_are_unchanged():
    burst = ParticleBurst((0.0, 0.0), random.Random(4))
    assert len(burst.particles) == 16
    assert burst.tint == "fruit"
    for p in burst.particles:
        assert 2.5 - 1e-9 <= (p.vx**2 + p.vy**2) ** 0.5 <= 7.5 + 1e-9
    burst.update(599)
    assert not burst.done
    burst.update(1)
    assert burst.done


# 005 / T003 — faixa de ângulos (chama do foguete aponta para baixo)
def test_particle_burst_angle_range():
    import math

    lo, hi = math.pi / 2 - 0.5, math.pi / 2 + 0.5
    burst = ParticleBurst((0.0, 0.0), random.Random(5), count=40, angle=(lo, hi))
    for p in burst.particles:
        a = math.atan2(p.vy, p.vx)
        assert lo - 1e-9 <= a <= hi + 1e-9
    spread = ParticleBurst((0.0, 0.0), random.Random(5), count=200)
    assert any(p.vy < 0 for p in spread.particles) and any(p.vy > 0 for p in spread.particles)
