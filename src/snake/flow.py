"""Fluxo de telas do jogo (inicial, contagem, partida, tremor, menu): lógica pura, sem Pygame nem relógio.

O tempo entra por `update(dt_ms)`; o adaptador só repassa teclado e relógio (Princípios I e III).
"""

import random
from enum import Enum

from snake.core import Direction, Game, Status
from snake.juice import ParticleBurst, ScorePulse, ScreenShake
from snake.menu import EndMenu, MenuOption

STEP_MS = 125  # 8 passos por segundo (001)
UI_ANIM_MS = 300
COUNTDOWN_MS = 3000


class Phase(Enum):
    TITLE_IN = "title_in"
    TITLE = "title"
    TITLE_OUT = "title_out"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    SHAKING = "shaking"
    MENU_IN = "menu_in"
    MENU = "menu"
    MENU_OUT = "menu_out"


class Flow:
    def __init__(self, seed: int | None = None, width: int = 20, height: int = 20) -> None:
        self.game = Game(width=width, height=height, rng=random.Random(seed))
        # RNG separado: efeitos não consomem números do jogo (SC-005), mas seguem a seed (FR-011)
        self._fx_rng = random.Random(f"juice-{seed}")
        self.bursts: list[ParticleBurst] = []
        self.pulse = ScorePulse()
        self.shake = ScreenShake(self._fx_rng)
        self.menu: EndMenu | None = None
        self.quit_requested = False
        self.phase = Phase.PLAYING
        self.phase_ms = 0.0
        self._step_elapsed = 0.0

    # --- entradas -------------------------------------------------------------------------

    def direction(self, direction: Direction) -> None:
        if self.phase is Phase.PLAYING:
            self.game.turn(direction)
        elif self.phase is Phase.MENU and self.menu is not None:
            if direction is Direction.UP:
                self.menu.move_up()
            elif direction is Direction.DOWN:
                self.menu.move_down()

    def confirm(self) -> None:
        if self.phase is Phase.MENU and self.menu is not None:
            if self.menu.confirm() is MenuOption.QUIT:
                self.quit_requested = True
            else:
                self.game.restart()
                self.menu = None
                self._go(Phase.PLAYING)

    def quit(self) -> None:
        self.quit_requested = True

    # --- tempo ----------------------------------------------------------------------------

    def update(self, dt_ms: float) -> None:
        self.phase_ms += dt_ms
        self._update_effects(dt_ms)
        if self.phase is Phase.PLAYING:
            self._update_playing(dt_ms)
        elif self.phase is Phase.SHAKING:
            self.shake.update(dt_ms)
            if self.shake.done:
                self._open_menu()

    def _update_effects(self, dt_ms: float) -> None:
        for burst in self.bursts:
            burst.update(dt_ms)
        self.bursts = [b for b in self.bursts if not b.done]
        self.pulse.update(dt_ms)

    def _update_playing(self, dt_ms: float) -> None:
        self._step_elapsed += dt_ms
        while self._step_elapsed >= STEP_MS and self.game.status is Status.RUNNING:
            self._step_elapsed -= STEP_MS
            score_before = self.game.score
            self.game.step()
            if self.game.score > score_before:
                self.bursts.append(ParticleBurst(self.game.snake[0], self._fx_rng))
                self.pulse.trigger()
        if self.game.status is Status.GAME_OVER:
            self.shake.trigger()
            self._go(Phase.SHAKING)
        elif self.game.status is Status.WON:
            self._open_menu()

    def _open_menu(self) -> None:
        self.menu = EndMenu()
        self._go(Phase.MENU)

    def _go(self, phase: Phase) -> None:
        self.phase = phase
        self.phase_ms = 0.0
        self._step_elapsed = 0.0
