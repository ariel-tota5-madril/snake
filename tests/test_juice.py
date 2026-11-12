import random

from snake.juice import ParticleBurst, ScorePulse, ease_out


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
