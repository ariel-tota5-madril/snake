"""Fluxo de telas do jogo (inicial, contagem, partida, tremor, menu): lógica pura, sem Pygame nem relógio.

O tempo entra por `update(dt_ms)`; o adaptador só repassa teclado e relógio (Princípios I e III).
Transições e entradas ignoradas seguem specs/002-game-juice/data-model.md.
"""

import random
from enum import Enum

from snake.core import Direction, Game, Status
from snake.juice import COLLISION_SHAKE, EAT_SHAKE, ParticleBurst, ScorePulse, ScreenShake, ease_out
from snake.menu import EndMenu, MenuOption

STEP_MS = 125  # 8 passos por segundo (001)
UI_ANIM_MS = 300
COUNTDOWN_MS = 3000
PULSE_POP_DELAY_MS = 60  # pico do pulso do placar (002)
GRID = 30  # grade 30x30 (FR-014); o padrão 20x20 do núcleo continua sendo o da 001


class SoundEvent(Enum):
    """O que deve soar; o Flow só avisa, quem toca é o adaptador de áudio (Princípio I)."""

    STEP = "step"
    EAT = "eat"
    PULSE_POP = "pulse_pop"
    CRASH = "crash"
    COUNT = "count"
    GO = "go"
    NAV = "nav"
    CONFIRM = "confirm"
    LOSE = "lose"
    WIN = "win"
    VOLUME_PREVIEW = "volume_preview"
    MUSIC_TITLE = "music_title"
    MUSIC_GAME = "music_game"
    MUSIC_STOP = "music_stop"
    MUSIC_DUCK = "music_duck"
    MUSIC_UNDUCK = "music_unduck"


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


ENTERING = {Phase.TITLE_IN, Phase.MENU_IN}
LEAVING = {Phase.TITLE_OUT, Phase.MENU_OUT}
TIMED_UI = {
    Phase.TITLE_IN: Phase.TITLE,
    Phase.TITLE_OUT: Phase.COUNTDOWN,
    Phase.MENU_IN: Phase.MENU,
}


class Flow:
    def __init__(self, seed: int | None = None, width: int = GRID, height: int = GRID) -> None:
        self.game = Game(width=width, height=height, rng=random.Random(seed))
        # RNG separado: efeitos não consomem números do jogo (SC-005), mas seguem a seed (FR-011)
        self._fx_rng = random.Random(f"juice-{seed}")
        self.bursts: list[ParticleBurst] = []
        self.pulse = ScorePulse()
        self.shake = ScreenShake(self._fx_rng)
        self.menu: EndMenu | None = None
        self.quit_requested = False
        self.phase = Phase.TITLE_IN
        self.phase_ms = 0.0
        self._step_elapsed = 0.0
        self._sounds: list[SoundEvent] = []
        self._pop_in_ms: float | None = None
        self._emit(SoundEvent.MUSIC_TITLE)

    # --- consultas ------------------------------------------------------------------------

    def drain_sounds(self) -> list[SoundEvent]:
        """Devolve os eventos sonoros acumulados desde a última chamada e limpa a fila."""
        sounds, self._sounds = self._sounds, []
        return sounds

    def _emit(self, event: SoundEvent) -> None:
        self._sounds.append(event)

    @property
    def countdown_number(self) -> int | None:
        if self.phase is not Phase.COUNTDOWN:
            return None
        return 3 - min(int(self.phase_ms // 1000), 2)

    @property
    def ui_progress(self) -> float:
        p = ease_out(self.phase_ms / UI_ANIM_MS)
        if self.phase in ENTERING:
            return p
        if self.phase in LEAVING:
            return 1 - p
        return 1.0

    # --- entradas -------------------------------------------------------------------------

    def direction(self, direction: Direction) -> None:
        if self.phase is Phase.PLAYING:
            self.game.turn(direction)
            return
        if self.phase is Phase.MENU_IN and direction in (Direction.UP, Direction.DOWN):
            self._go(Phase.MENU)  # tecla do menu conclui a entrada (FR-009)
        if self.phase is Phase.MENU and self.menu is not None:
            if direction is Direction.UP:
                self.menu.move_up()
            elif direction is Direction.DOWN:
                self.menu.move_down()

    def confirm(self) -> None:
        if self.phase is Phase.TITLE:
            self._go(Phase.TITLE_OUT)
            return
        if self.phase is Phase.MENU_IN:
            self._go(Phase.MENU)  # conclui a entrada e trata a tecla (FR-009)
        if self.phase is Phase.MENU and self.menu is not None:
            if self.menu.confirm() is MenuOption.QUIT:
                self.quit_requested = True
            else:
                self._go(Phase.MENU_OUT)

    def quit(self) -> None:
        self.quit_requested = True

    # --- tempo ----------------------------------------------------------------------------

    def update(self, dt_ms: float) -> None:
        self.phase_ms += dt_ms
        self._update_effects(dt_ms)
        if self.phase in TIMED_UI and self.phase_ms >= UI_ANIM_MS:
            self._go(TIMED_UI[self.phase])
        elif self.phase is Phase.MENU_OUT and self.phase_ms >= UI_ANIM_MS:
            self.game.restart()
            self.menu = None
            self._go(Phase.COUNTDOWN)
        elif self.phase is Phase.COUNTDOWN and self.phase_ms >= COUNTDOWN_MS:
            self._go(Phase.PLAYING)
            self._emit(SoundEvent.MUSIC_GAME)
            self._step_once()  # a cobra anda assim que a contagem termina (SC-003)
            self._check_end()
        elif self.phase is Phase.PLAYING:
            self._update_playing(dt_ms)
        elif self.phase is Phase.SHAKING and self.shake.done:
            self._open_menu()

    def _update_effects(self, dt_ms: float) -> None:
        for burst in self.bursts:
            burst.update(dt_ms)
        self.bursts = [b for b in self.bursts if not b.done]
        self.pulse.update(dt_ms)
        self.shake.update(dt_ms)
        if self._pop_in_ms is not None:
            self._pop_in_ms -= dt_ms
            if self._pop_in_ms <= 0:
                self._pop_in_ms = None
                self._emit(SoundEvent.PULSE_POP)

    def _update_playing(self, dt_ms: float) -> None:
        self._step_elapsed += dt_ms
        while self._step_elapsed >= STEP_MS and self.game.status is Status.RUNNING:
            self._step_elapsed -= STEP_MS
            self._step_once()
        self._check_end()

    def _step_once(self) -> None:
        score_before = self.game.score
        self.game.step()
        if self.game.status is Status.RUNNING:
            self._emit(SoundEvent.STEP)
        if self.game.score > score_before:
            self.bursts.append(ParticleBurst(self.game.snake[0], self._fx_rng))
            self.pulse.trigger()
            self.shake.trigger(*EAT_SHAKE)
            self._emit(SoundEvent.EAT)
            self._pop_in_ms = PULSE_POP_DELAY_MS

    def _check_end(self) -> None:
        if self.game.status is Status.GAME_OVER:
            self.shake.trigger(*COLLISION_SHAKE)
            self._emit(SoundEvent.CRASH)
            self._emit(SoundEvent.MUSIC_STOP)
            self._go(Phase.SHAKING)
        elif self.game.status is Status.WON:
            self._emit(SoundEvent.MUSIC_STOP)
            self._open_menu()

    def _open_menu(self) -> None:
        self._emit(SoundEvent.LOSE if self.game.status is Status.GAME_OVER else SoundEvent.WIN)
        self.menu = EndMenu()
        self._go(Phase.MENU_IN)

    def _go(self, phase: Phase) -> None:
        self.phase = phase
        self.phase_ms = 0.0
        self._step_elapsed = 0.0
