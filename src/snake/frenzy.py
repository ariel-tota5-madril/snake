"""Feeding Frenzy e velocidade progressiva: regras puras, sem Pygame nem relógio.

Curva de velocidade (FR-002/FR-006), limiares do modo (FR-004) e o cronômetro de 20 s (FR-008),
que só anda quando o Flow repassa `dt` em PLAYING.
"""

BASE_STEP_MS = 125
MIN_STEP_MS = 70
START_LENGTH = 3
FRENZY_SPEEDUP = 1.5
FRENZY_MIN_STEP_MS = 50
FIRST_THRESHOLD = 10
FRENZY_MS = 20_000
SPECIAL_COUNT = 10
WARNING_SECONDS = 5


def step_interval_ms(length: int, frenzy: bool = False) -> float:
    """Intervalo entre passos para uma cobra com `length` segmentos (FR-002).

    No Frenzy, a cobra anda 1,5× mais rápido, nunca abaixo de 50 ms por passo (FR-006).
    """
    normal = max(MIN_STEP_MS, BASE_STEP_MS - (length - START_LENGTH))
    if frenzy:
        return max(FRENZY_MIN_STEP_MS, normal / FRENZY_SPEEDUP)
    return normal


def threshold(n: int) -> int:
    """Placar do n-ésimo Feeding Frenzy (n = 0, 1, 2…): 10, 20, 40, 80… (FR-004)."""
    return FIRST_THRESHOLD * 2**n


def _ceil_seconds(ms: float) -> int:
    return -int(-ms // 1000)


class Frenzy:
    """Cronômetro do modo: só anda quando recebe `dt` (o Flow chama apenas em PLAYING)."""

    def __init__(self, duration_ms: float = FRENZY_MS) -> None:
        self.remaining_ms = float(duration_ms)

    def update(self, dt_ms: float) -> list[int]:
        """Desconta `dt` e devolve os segundos de aviso (5…1) que começaram agora, em ordem."""
        before = self.seconds_left
        self.remaining_ms = max(0.0, self.remaining_ms - dt_ms)
        after = self.seconds_left
        return [s for s in range(before - 1, after - 1, -1) if 1 <= s <= WARNING_SECONDS]

    @property
    def seconds_left(self) -> int:
        return _ceil_seconds(self.remaining_ms)

    @property
    def warning(self) -> bool:
        return 0 < self.seconds_left <= WARNING_SECONDS

    @property
    def expired(self) -> bool:
        return self.remaining_ms == 0
