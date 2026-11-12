"""Fluxo de telas do jogo: lógica pura, sem Pygame nem relógio.

Telas: inicial, contagem, partida, tremor, fim de partida (002), pausa, retomada e Opções (003).
O tempo entra por `update(dt_ms)`; o adaptador só repassa teclado e relógio (Princípios I e III).
O Flow não toca som: ele só registra eventos sonoros que o adaptador de áudio consome.
Transições seguem specs/002-game-juice/data-model.md e specs/003-audio-sfx-bgm/data-model.md.
"""

import random
from enum import Enum
from pathlib import Path

from snake.core import Direction, Game, Status
from snake.juice import COLLISION_SHAKE, EAT_SHAKE, ParticleBurst, ScorePulse, ScreenShake, ease_out
from snake.menu import (
    PAUSE_OPTIONS,
    SETTINGS_OPTIONS,
    TITLE_OPTIONS,
    EndMenu,
    Menu,
    MenuOption,
)
from snake.settings import AudioSettings

STEP_MS = 125  # 8 passos por segundo (001)
UI_ANIM_MS = 300
COUNTDOWN_MS = 3000
RESUME_MS = 1500  # contagem rápida ao sair da pausa (003)
RESUME_STEP_MS = 500
PULSE_POP_DELAY_MS = 60  # pico do pulso do placar (002)
GRID = 30  # grade 30x30 (FR-014 da 002); o padrão 20x20 do núcleo continua sendo o da 001


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
    PAUSE_IN = "pause_in"
    PAUSE = "pause"
    PAUSE_OUT = "pause_out"
    RESUME = "resume"
    OPTIONS_IN = "options_in"
    OPTIONS = "options"
    OPTIONS_OUT = "options_out"


ENTERING = {Phase.TITLE_IN, Phase.MENU_IN, Phase.PAUSE_IN, Phase.OPTIONS_IN}
LEAVING = {Phase.TITLE_OUT, Phase.MENU_OUT, Phase.PAUSE_OUT, Phase.OPTIONS_OUT}
ENTRANCE_DONE = {
    Phase.TITLE_IN: Phase.TITLE,
    Phase.MENU_IN: Phase.MENU,
    Phase.PAUSE_IN: Phase.PAUSE,
    Phase.OPTIONS_IN: Phase.OPTIONS,
}
PAUSE_PHASES = {Phase.PAUSE_IN, Phase.PAUSE, Phase.PAUSE_OUT, Phase.RESUME}
OPTIONS_PHASES = {Phase.OPTIONS_IN, Phase.OPTIONS, Phase.OPTIONS_OUT}
VOLUME_FIELDS = {MenuOption.MUSIC: "music", MenuOption.SFX: "sfx"}


class Flow:
    def __init__(
        self,
        seed: int | None = None,
        width: int = GRID,
        height: int = GRID,
        settings: AudioSettings | None = None,
        settings_path: Path | None = None,
    ) -> None:
        self.game = Game(width=width, height=height, rng=random.Random(seed))
        # RNG separado: efeitos não consomem números do jogo (SC-005), mas seguem a seed (FR-011)
        self._fx_rng = random.Random(f"juice-{seed}")
        self.bursts: list[ParticleBurst] = []
        self.pulse = ScorePulse()
        self.shake = ScreenShake(self._fx_rng)
        self.settings_path = settings_path
        if settings is None:
            settings = AudioSettings.load(settings_path) if settings_path else AudioSettings()
        self.settings = settings
        self.menu: EndMenu | None = None
        self.title_menu: Menu | None = None
        self.pause_menu: Menu | None = None
        self.options_menu: Menu | None = None
        self.quit_requested = False
        self.phase = Phase.TITLE_IN
        self.phase_ms = 0.0
        self._step_elapsed = 0.0
        self._sounds: list[SoundEvent] = []
        self._pop_in_ms: float | None = None
        self._options_origin = Phase.TITLE
        self._pause_exit = MenuOption.CONTINUE
        self._enter_title()

    # --- consultas ------------------------------------------------------------------------

    def drain_sounds(self) -> list[SoundEvent]:
        """Devolve os eventos sonoros acumulados desde a última chamada e limpa a fila."""
        sounds, self._sounds = self._sounds, []
        return sounds

    @property
    def countdown_number(self) -> int | None:
        if self.phase is not Phase.COUNTDOWN:
            return None
        return 3 - min(int(self.phase_ms // 1000), 2)

    @property
    def resume_number(self) -> int | None:
        if self.phase is not Phase.RESUME:
            return None
        return 3 - min(int(self.phase_ms // RESUME_STEP_MS), 2)

    @property
    def ui_progress(self) -> float:
        p = ease_out(self.phase_ms / UI_ANIM_MS)
        if self.phase in ENTERING:
            return p
        if self.phase in LEAVING:
            return 1 - p
        return 1.0

    @property
    def options_origin(self) -> Phase:
        """Tela de onde as Opções foram abertas (TITLE, PAUSE ou MENU)."""
        return self._options_origin

    @property
    def game_frozen(self) -> bool:
        """Na pausa (e nas Opções abertas pela pausa) o tempo do jogo e dos efeitos não anda."""
        return self.phase in PAUSE_PHASES or (
            self.phase in OPTIONS_PHASES and self._options_origin is Phase.PAUSE
        )

    # --- entradas -------------------------------------------------------------------------

    def direction(self, direction: Direction) -> None:
        if self.phase is Phase.PLAYING:
            self.game.turn(direction)
            return
        if self.phase in (Phase.MENU_IN, Phase.PAUSE_IN, Phase.OPTIONS_IN):
            self._go(ENTRANCE_DONE[self.phase])  # tecla do menu conclui a entrada (FR-009 da 002)
        menu = self._active_menu()
        if menu is None:
            return
        if direction is Direction.UP:
            menu.move_up()
        elif direction is Direction.DOWN:
            menu.move_down()
        elif self.phase is Phase.OPTIONS and menu.selected in VOLUME_FIELDS:
            self.settings.adjust(VOLUME_FIELDS[menu.selected], 1 if direction is Direction.RIGHT else -1)

    def confirm(self) -> None:
        if self.phase in (Phase.MENU_IN, Phase.PAUSE_IN, Phase.OPTIONS_IN):
            self._go(ENTRANCE_DONE[self.phase])  # conclui a entrada e trata a tecla
        if self.phase is Phase.TITLE:
            if self.title_menu.confirm() is MenuOption.PLAY:
                self._go(Phase.TITLE_OUT)
            else:
                self._open_options(Phase.TITLE)
        elif self.phase is Phase.MENU and self.menu is not None:
            choice = self.menu.confirm()
            if choice is MenuOption.QUIT:
                self.quit_requested = True
            elif choice is MenuOption.OPTIONS:
                self._open_options(Phase.MENU)
            else:
                self._go(Phase.MENU_OUT)
        elif self.phase is Phase.PAUSE:
            choice = self.pause_menu.confirm()
            if choice is MenuOption.OPTIONS:
                self._open_options(Phase.PAUSE)
            else:
                self._leave_pause(choice)
        elif self.phase is Phase.OPTIONS and self.options_menu.selected is MenuOption.BACK:
            self._leave_options()

    def escape(self) -> None:
        if self.phase is Phase.PLAYING:
            self.pause_menu = Menu(PAUSE_OPTIONS)
            self._emit(SoundEvent.MUSIC_DUCK)
            self._go(Phase.PAUSE_IN)
        elif self.phase in (Phase.PAUSE_IN, Phase.PAUSE):
            self._leave_pause(MenuOption.CONTINUE)
        elif self.phase in (Phase.OPTIONS_IN, Phase.OPTIONS):
            self._leave_options()

    def quit(self) -> None:
        self.quit_requested = True

    # --- tempo ----------------------------------------------------------------------------

    def update(self, dt_ms: float) -> None:
        self.phase_ms += dt_ms
        if not self.game_frozen:
            self._update_effects(dt_ms)
        if self.phase in ENTRANCE_DONE and self.phase_ms >= UI_ANIM_MS:
            self._go(ENTRANCE_DONE[self.phase])
        elif self.phase is Phase.TITLE_OUT and self.phase_ms >= UI_ANIM_MS:
            self._go(Phase.COUNTDOWN)
        elif self.phase is Phase.MENU_OUT and self.phase_ms >= UI_ANIM_MS:
            self.game.restart()
            self.menu = None
            self._go(Phase.COUNTDOWN)
        elif self.phase is Phase.PAUSE_OUT and self.phase_ms >= UI_ANIM_MS:
            self._finish_leaving_pause()
        elif self.phase is Phase.OPTIONS_OUT and self.phase_ms >= UI_ANIM_MS:
            self.options_menu = None
            self._go(self._options_origin)
        elif self.phase is Phase.COUNTDOWN and self.phase_ms >= COUNTDOWN_MS:
            self._go(Phase.PLAYING)
            self._emit(SoundEvent.MUSIC_GAME)
            self._step_once()  # a cobra anda assim que a contagem termina (SC-003 da 002)
            self._check_end()
        elif self.phase is Phase.RESUME and self.phase_ms >= RESUME_MS:
            self._go(Phase.PLAYING)  # sem passo imediato nem passos acumulados
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
        if self.phase is not Phase.PLAYING:
            return
        if self.game.status is Status.GAME_OVER:
            self.shake.trigger(*COLLISION_SHAKE)
            self._emit(SoundEvent.CRASH)
            self._emit(SoundEvent.MUSIC_STOP)
            self._go(Phase.SHAKING)
        elif self.game.status is Status.WON:
            self._emit(SoundEvent.MUSIC_STOP)
            self._open_menu()

    # --- transições de tela ---------------------------------------------------------------

    def _active_menu(self) -> Menu | None:
        return {
            Phase.TITLE: self.title_menu,
            Phase.MENU: self.menu,
            Phase.PAUSE: self.pause_menu,
            Phase.OPTIONS: self.options_menu,
        }.get(self.phase)

    def _enter_title(self) -> None:
        self.title_menu = Menu(TITLE_OPTIONS)
        self._emit(SoundEvent.MUSIC_TITLE)
        self._go(Phase.TITLE_IN)

    def _open_menu(self) -> None:
        self._emit(SoundEvent.LOSE if self.game.status is Status.GAME_OVER else SoundEvent.WIN)
        self.menu = EndMenu()
        self._go(Phase.MENU_IN)

    def _open_options(self, origin: Phase) -> None:
        self._options_origin = origin
        self.options_menu = Menu(SETTINGS_OPTIONS)
        self._go(Phase.OPTIONS_IN)

    def _leave_options(self) -> None:
        if self.settings_path is not None:
            self.settings.save(self.settings_path)
        self._go(Phase.OPTIONS_OUT)

    def _leave_pause(self, choice: MenuOption) -> None:
        self._pause_exit = choice
        if choice is MenuOption.CONTINUE:
            self._emit(SoundEvent.MUSIC_UNDUCK)
        else:
            self._emit(SoundEvent.MUSIC_STOP)
        self._go(Phase.PAUSE_OUT)

    def _finish_leaving_pause(self) -> None:
        self.pause_menu = None
        if self._pause_exit is MenuOption.CONTINUE:
            self._go(Phase.RESUME)
            return
        # "Tela inicial": abandona a partida e volta ao começo
        self.game.restart()
        self.bursts = []
        self.pulse = ScorePulse()
        self.shake = ScreenShake(self._fx_rng)
        self._pop_in_ms = None
        self._enter_title()

    def _go(self, phase: Phase) -> None:
        self.phase = phase
        self.phase_ms = 0.0
        self._step_elapsed = 0.0

    def _emit(self, event: SoundEvent) -> None:
        self._sounds.append(event)
