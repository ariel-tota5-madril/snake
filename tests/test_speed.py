from snake.frenzy import step_interval_ms


# 004 / T005 — FR-002: 125 ms com 3 segmentos, −1 ms por segmento, mínimo de 70 ms
def test_normal_curve_values():
    assert step_interval_ms(3) == 125
    assert step_interval_ms(4) == 124
    assert step_interval_ms(13) == 115
    assert step_interval_ms(58) == 70
    assert step_interval_ms(100) == 70


def test_normal_curve_never_gets_slower_as_the_snake_grows():
    values = [step_interval_ms(n) for n in range(3, 200)]
    assert values == sorted(values, reverse=True)
    assert min(values) == 70


# 004 / T010 — FR-006: no Frenzy, 1,5× mais rápido, nunca abaixo de 50 ms
def test_frenzy_bonus_values():
    assert abs(step_interval_ms(13, frenzy=True) - 115 / 1.5) < 1e-9
    assert step_interval_ms(100, frenzy=True) == 50


def test_frenzy_is_never_slower_than_normal():
    for n in range(3, 200):
        assert step_interval_ms(n, frenzy=True) <= step_interval_ms(n)
