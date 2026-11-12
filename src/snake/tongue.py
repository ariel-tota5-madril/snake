"""Língua de Yoshi: recarga e animação de ida e volta. Lógica pura, sem Pygame nem relógio.

A regra do disparo (alcance, bloqueio, coleta) vive no núcleo (`Game.tongue`); aqui fica só o
tempo: recarga de 8 s (006/FR-004) e a animação visual de 300 ms (FR-006).
"""

COOLDOWN_MS = 8000
REACH = 3
ANIM_MS = 300


class Tongue:
    """Recarga de 8 s e animação de 300 ms (150 ms de ida, 150 ms de volta)."""

    def __init__(self) -> None:
        self.remaining_ms = 0.0  # 0 = pronta (FR-013: toda partida começa com a língua pronta)
        self.shot = None
        self._anim_ms: float | None = None

    @property
    def ready(self) -> bool:
        return self.remaining_ms == 0

    @property
    def progress(self) -> float:
        """0 logo após o disparo, 1 quando pronta (o relógio do ícone)."""
        return 1 - self.remaining_ms / COOLDOWN_MS

    def fire(self, shot) -> None:
        self.shot = shot
        self.remaining_ms = float(COOLDOWN_MS)
        self._anim_ms = 0.0

    def update_cooldown(self, dt_ms: float) -> bool:
        """Desconta a recarga; True apenas no update em que ela termina."""
        if self.remaining_ms == 0:
            return False
        self.remaining_ms = max(0.0, self.remaining_ms - dt_ms)
        return self.remaining_ms == 0

    def update_anim(self, dt_ms: float) -> None:
        if self._anim_ms is None:
            return
        self._anim_ms += dt_ms
        if self._anim_ms >= ANIM_MS:
            self._anim_ms = None

    @property
    def extension(self) -> float:
        """0 -> 1 na ida, 1 -> 0 na volta; 0 fora da animação."""
        if self._anim_ms is None:
            return 0.0
        half = ANIM_MS / 2
        t = self._anim_ms
        return t / half if t <= half else max(0.0, (ANIM_MS - t) / half)

    @property
    def retracting(self) -> bool:
        """Na volta da língua (a fruta comida vem presa na ponta)."""
        return self._anim_ms is not None and self._anim_ms > ANIM_MS / 2
