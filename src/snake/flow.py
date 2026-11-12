"""Fluxo de telas do jogo: lógica pura, sem Pygame nem relógio.

Telas: inicial, contagem, partida, tremor, fim de partida (002), pausa, retomada e Opções (003).
O tempo entra por `update(dt_ms)`; o adaptador só repassa teclado e relógio (Princípios I e III).
O Flow não toca som: ele só registra eventos sonoros que o adaptador de áudio consome.
Transições seguem specs/002-game-juice/data-model.md e specs/003-audio-sfx-bgm/data-model.md.
"""

import math
import random
from enum import Enum
from pathlib import Path

from snake.core import Direction, Game, Status
from snake.highscores import Entry, Highscores
from snake.tongue import REACH, Tongue
from snake.frenzy import SPECIAL_COUNT, Frenzy, step_interval_ms, threshold
from snake.juice import (
    COLLISION_SHAKE,
    EAT_SHAKE,
    STAMP_SHAKE,
    ParticleBurst,
    ScorePulse,
    ScreenShake,
    ease_in,
    ease_in_out,
    ease_out,
)
from snake.menu import (
    PAUSE_OPTIONS,
    SETTINGS_OPTIONS,
    TITLE_OPTIONS,
    EndMenu,
    Menu,
    MenuOption,
    NameEntry,
)
from snake.scoreboard import Scoreboard
from snake.settings import AudioSettings

STEP_MS = 125  # intervalo inicial (001); na 004 o passo segue frenzy.step_interval_ms
UI_ANIM_MS = 300
COUNTDOWN_MS = 3000
RESUME_MS = 1500  # contagem rápida ao sair da pausa (003)
RESUME_STEP_MS = 500
PULSE_POP_DELAY_MS = 60  # pico do pulso do placar (002)
TIMEOUT_MS = 1200  # 004: "0" piscando + alarme antes do menu de fim
TIMEOUT_BLINK_MS = 150
SPECIAL_TINTS = ("purple", "gold")  # variante da fruta especial -> rótulo de cor
# Abertura do Frenzy (research.md §6 da 004): duas palavras carimbadas na diagonal
INTRO_MS = 1900
STAMP_DROP_AT = (200, 800)  # início da queda de "FEEDING" e de "FRENZY"
STAMP_DROP_MS = 300
STAMP_START_SCALE = 4.0
STAMP_FADE_AT, STAMP_FADE_MS = 1600, 300
STAMP_ANGLE_DEG = 15  # sobe para a direita
STAMP_OFFSET = (3.0, 2.5)  # deslocamento (em casas) de cada palavra em relação ao centro
STAMP_HALF_LENGTH = 5.0  # meia largura da palavra, em casas: onde os detritos se espalham
SURVIVED_MS = 1500  # "SURVIVED!": entra em 500 ms, fica até 1 000 ms, sai até 1 500 ms
SURVIVED_IN_MS, SURVIVED_OUT_AT = 500, 1000
DEBRIS_BURSTS, DEBRIS_COUNT, DEBRIS_SPEED, DEBRIS_LIFE_MS = 5, 12, (6, 14), 900
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
    TIMER_TICK = "timer_tick"  # 004: últimos 5 s do Frenzy
    TIMEOUT_ALARM = "timeout_alarm"  # 004: tempo do Frenzy esgotado
    MUSIC_FRENZY = "music_frenzy"  # 004: música tensa do Frenzy
    BOOM = "boom"  # 004: impacto de cada palavra da abertura
    NAME_TYPE = "name_type"  # 005: digitar/apagar no nome
    ROCKET_IGNITE = "rocket_ignite"  # 005: animação do placar
    ROCKET_LAUNCH = "rocket_launch"
    ROCKET_HIT = "rocket_hit"
    ROCKET_LAND = "rocket_land"
    FIRST_PLACE = "first_place"
    TONGUE = "tongue"  # 006: disparo da língua
    TONGUE_READY = "tongue_ready"  # 006: recarga terminou


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
    TIMEOUT = "timeout"  # 004: tempo do Frenzy esgotado
    FRENZY_INTRO = "frenzy_intro"  # 004: "FEEDING" / "FRENZY" carimbadas
    SURVIVED = "survived"  # 004: "SURVIVED!" ao superar o Frenzy
    NAME_IN = "name_in"  # 005: entrada do nome do jogador
    NAME = "name"
    NAME_OUT = "name_out"
    RANKING_IN = "ranking_in"  # 005: consulta do placar pela tela inicial
    RANKING = "ranking"
    RANKING_OUT = "ranking_out"


SCOREBOARD_SOUNDS = {  # eventos da animação do placar -> sons (005)
    "ignite": SoundEvent.ROCKET_IGNITE,
    "launch": SoundEvent.ROCKET_LAUNCH,
    "hit": SoundEvent.ROCKET_HIT,
    "land": SoundEvent.ROCKET_LAND,
    "first": SoundEvent.FIRST_PLACE,
}
ENTERING = {Phase.TITLE_IN, Phase.MENU_IN, Phase.PAUSE_IN, Phase.OPTIONS_IN, Phase.NAME_IN, Phase.RANKING_IN}
LEAVING = {Phase.TITLE_OUT, Phase.MENU_OUT, Phase.PAUSE_OUT, Phase.OPTIONS_OUT, Phase.NAME_OUT, Phase.RANKING_OUT}
ENTRANCE_DONE = {
    Phase.RANKING_IN: Phase.RANKING,
    Phase.NAME_IN: Phase.NAME,
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
        highscores_path: Path | None = None,
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
        self._last_number: int | None = None
        self.frenzy: Frenzy | None = None  # cronômetro do Feeding Frenzy (004)
        self.frenzy_count = 0
        self.timer_pulse = ScorePulse()
        self._impacts = 0
        self.name_entry: NameEntry | None = None  # 005
        self.player_name: str | None = None
        self.highscores_path = highscores_path
        self.highscores = Highscores.load(highscores_path) if highscores_path else Highscores()
        self.scoreboard: Scoreboard | None = None
        self.ranking: Scoreboard | None = None  # consulta pela tela inicial (FR-010b)
        self._end_choice = MenuOption.PLAY_AGAIN
        self.tongue = Tongue()  # 006: língua de Yoshi
        self.icon_pulse = ScorePulse()
        self._ready_announced = True  # a partida começa com a língua pronta, sem som
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
    def tongue_locked(self) -> bool:
        """Sem língua no Feeding Frenzy (006/FR-005): o ícone fica acinzentado."""
        return self.game.in_frenzy

    @property
    def accepts_text(self) -> bool:
        """Na entrada de nome, letras são texto (o adaptador não as trata como WASD)."""
        return self.phase in (Phase.NAME_IN, Phase.NAME)

    @property
    def options_origin(self) -> Phase:
        """Tela de onde as Opções foram abertas (TITLE, PAUSE ou MENU)."""
        return self._options_origin

    @property
    def timer_visible(self) -> bool:
        """Cronômetro do Frenzy na tela: com o modo ativo (inclusive pausado) e no tempo esgotado."""
        return self.frenzy is not None and self.phase is not Phase.FRENZY_INTRO

    @property
    def timeout_blink(self) -> bool:
        """No tempo esgotado, o "0" vermelho alterna aceso/apagado a cada 150 ms."""
        return self.phase is Phase.TIMEOUT and int(self.phase_ms // TIMEOUT_BLINK_MS) % 2 == 0

    @property
    def stamp_origins(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Centro (em casas) de "FEEDING" (acima/esquerda) e "FRENZY" (abaixo/direita)."""
        cx, cy = self.game.width / 2, self.game.height / 2
        ox, oy = STAMP_OFFSET
        return (cx - ox, cy - oy), (cx + ox, cy + oy)

    @property
    def stamp_scales(self) -> tuple[float | None, float | None]:
        """Escala de cada palavra na abertura: None antes de entrar, 4x caindo até 1x."""
        if self.phase is not Phase.FRENZY_INTRO:
            return (None, None)
        scales = []
        for start in STAMP_DROP_AT:
            if self.phase_ms < start:
                scales.append(None)
            else:
                t = (self.phase_ms - start) / STAMP_DROP_MS
                scales.append(STAMP_START_SCALE - (STAMP_START_SCALE - 1) * ease_in(t))
        return tuple(scales)

    @property
    def stamp_alpha(self) -> float:
        if self.phase is not Phase.FRENZY_INTRO:
            return 0.0
        return 1.0 - min(max((self.phase_ms - STAMP_FADE_AT) / STAMP_FADE_MS, 0.0), 1.0)

    @property
    def survived_progress(self) -> float:
        """0 → 1 na entrada suave, 1 enquanto fica, 1 → 0 na saída; 0 fora de SURVIVED."""
        if self.phase is not Phase.SURVIVED:
            return 0.0
        if self.phase_ms < SURVIVED_IN_MS:
            return ease_in_out(self.phase_ms / SURVIVED_IN_MS)
        if self.phase_ms < SURVIVED_OUT_AT:
            return 1.0
        return 1 - ease_in_out((self.phase_ms - SURVIVED_OUT_AT) / (SURVIVED_MS - SURVIVED_OUT_AT))

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
        if self.phase in (Phase.MENU_IN, Phase.PAUSE_IN, Phase.OPTIONS_IN, Phase.RANKING_IN):
            self._go(ENTRANCE_DONE[self.phase])  # tecla do menu conclui a entrada (FR-009 da 002)
        if self.phase is Phase.RANKING:
            if direction in (Direction.UP, Direction.DOWN):
                if self.ranking.scroll(-1 if direction is Direction.UP else 1):
                    self._emit(SoundEvent.NAV)
            return
        if self.phase is Phase.MENU:
            self._scoreboard_direction(direction)
            return
        menu = self._active_menu()
        if menu is None:
            return
        if direction in (Direction.UP, Direction.DOWN):
            moved = menu.move_up() if direction is Direction.UP else menu.move_down()
            if moved:
                self._emit(SoundEvent.NAV)  # só toca quando a seleção muda (FR-009)
        elif self.phase is Phase.OPTIONS and menu.selected in VOLUME_FIELDS:
            field = VOLUME_FIELDS[menu.selected]
            if self.settings.adjust(field, 1 if direction is Direction.RIGHT else -1):
                self._emit(SoundEvent.VOLUME_PREVIEW if field == "sfx" else SoundEvent.NAV)

    def space(self) -> None:
        """Espaço: na partida dispara a língua (006/FR-001); nas outras telas confirma."""
        if self.phase is not Phase.PLAYING:
            self.confirm()
            return
        if self.tongue_locked or not self.tongue.ready:
            return  # em recarga ou no Frenzy: nada acontece, sem som
        shot = self.game.tongue(REACH)
        self.tongue.fire(shot)
        self._ready_announced = False
        self._emit(SoundEvent.TONGUE)
        if shot.ate:
            self._eat_effects(self.game.snake[0])
        self._check_end()

    def type_text(self, ch: str) -> None:
        """Texto digitado na entrada de nome (005/FR-002)."""
        if self.phase is Phase.NAME_IN:
            self._go(Phase.NAME)  # digitar conclui a entrada
        if self.phase is Phase.NAME and self.name_entry.type(ch):
            self._emit(SoundEvent.NAME_TYPE)

    def backspace(self) -> None:
        if self.phase is Phase.NAME_IN:
            self._go(Phase.NAME)
        if self.phase is Phase.NAME and self.name_entry.backspace():
            self._emit(SoundEvent.NAME_TYPE)

    def confirm(self) -> None:
        if self.phase in (Phase.MENU_IN, Phase.PAUSE_IN, Phase.OPTIONS_IN, Phase.NAME_IN):
            self._go(ENTRANCE_DONE[self.phase])  # conclui a entrada e trata a tecla
        if self.phase is Phase.NAME:
            if self.name_entry.confirmable:  # nome vazio não começa partida
                self.player_name = self.name_entry.value
                self._emit(SoundEvent.CONFIRM)
                self._go(Phase.NAME_OUT)
            return
        if self.phase in (Phase.RANKING_IN, Phase.RANKING):
            self._emit(SoundEvent.CONFIRM)
            self._go(Phase.RANKING_OUT)
            return
        if self.phase is Phase.MENU:
            if not self.scoreboard.done:
                self.scoreboard.skip()  # Enter pula a animação (005/FR-015)
                return
            self._emit(SoundEvent.CONFIRM)
            self._leave_scoreboard(self.menu.confirm())
            return
        if self.phase in (Phase.TITLE, Phase.PAUSE) or (
            self.phase is Phase.OPTIONS and self.options_menu.selected is MenuOption.BACK
        ):
            self._emit(SoundEvent.CONFIRM)
        if self.phase is Phase.TITLE:
            choice = self.title_menu.confirm()
            if choice is MenuOption.PLAY:
                self._go(Phase.TITLE_OUT)
            elif choice is MenuOption.RANKING:
                self.ranking = Scoreboard.viewer(self.highscores.entries, self._fx_rng)
                self._go(Phase.RANKING_IN)
            elif choice is MenuOption.QUIT:
                self.quit_requested = True
            else:
                self._open_options(Phase.TITLE)
        elif self.phase is Phase.PAUSE:
            choice = self.pause_menu.confirm()
            if choice is MenuOption.OPTIONS:
                self._open_options(Phase.PAUSE)
            else:
                self._leave_pause(choice)
        elif self.phase is Phase.OPTIONS and self.options_menu.selected is MenuOption.BACK:
            self._leave_options()

    def escape(self) -> None:
        if self.phase in (Phase.RANKING_IN, Phase.RANKING):
            self._go(Phase.RANKING_OUT)
        elif self.phase in (Phase.MENU_IN, Phase.MENU):
            self._leave_scoreboard(MenuOption.TITLE)  # Esc no placar = "Tela inicial"
        elif self.phase in (Phase.NAME_IN, Phase.NAME):
            self.name_entry = None
            self.title_menu = Menu(TITLE_OPTIONS)
            self._go(Phase.TITLE_IN)  # a música da tela inicial continua tocando
        elif self.phase is Phase.PLAYING:
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
            self.name_entry = NameEntry(self.player_name or "")  # 005: pede o nome
            self._go(Phase.NAME_IN)
        elif self.phase is Phase.RANKING_OUT and self.phase_ms >= UI_ANIM_MS:
            self.ranking = None
            self._go(Phase.TITLE)  # a música da tela inicial continua
        elif self.phase is Phase.NAME_OUT and self.phase_ms >= UI_ANIM_MS:
            self.name_entry = None
            self._go(Phase.COUNTDOWN)
        elif self.phase is Phase.MENU_OUT and self.phase_ms >= UI_ANIM_MS:
            self.menu = None
            self.scoreboard = None
            if self._end_choice is MenuOption.PLAY_AGAIN:
                self.game.restart()
                self._reset_round()
                self._go(Phase.COUNTDOWN)  # mesmo nome, sem pedir de novo (FR-004)
            else:
                self._back_to_title()
        elif self.phase is Phase.MENU:
            self._update_scoreboard(dt_ms)
        elif self.phase is Phase.PAUSE_OUT and self.phase_ms >= UI_ANIM_MS:
            self._finish_leaving_pause()
        elif self.phase is Phase.OPTIONS_OUT and self.phase_ms >= UI_ANIM_MS:
            self.options_menu = None
            self._go(self._options_origin)
        elif self.phase is Phase.COUNTDOWN and self.phase_ms >= COUNTDOWN_MS:
            self._go(Phase.PLAYING)
            self._emit(SoundEvent.GO)
            self._emit(SoundEvent.MUSIC_GAME)
            self._step_once()  # a cobra anda assim que a contagem termina (SC-003 da 002)
            self._check_end()
        elif self.phase is Phase.RESUME and self.phase_ms >= RESUME_MS:
            self._go(Phase.PLAYING)  # sem passo imediato nem passos acumulados
            self._emit(SoundEvent.GO)
        elif self.phase is Phase.TIMEOUT and self.phase_ms >= TIMEOUT_MS:
            self._open_menu()
        elif self.phase is Phase.FRENZY_INTRO:
            self._update_intro()
        elif self.phase is Phase.SURVIVED and self.phase_ms >= SURVIVED_MS:
            self._go(Phase.PLAYING)  # sem passo imediato, como na retomada da pausa
            self._emit(SoundEvent.MUSIC_GAME)
        elif self.phase is Phase.PLAYING:
            self._update_playing(dt_ms)
        elif self.phase is Phase.SHAKING and self.shake.done:
            self._open_menu()
        self._beep_on_new_number()

    def _beep_on_new_number(self) -> None:
        """Bipe a cada número novo da contagem inicial e da retomada (FR-008)."""
        number = self.countdown_number or self.resume_number
        if number is not None and number != self._last_number:
            self._emit(SoundEvent.COUNT)
        self._last_number = number

    def _update_effects(self, dt_ms: float) -> None:
        for burst in self.bursts:
            burst.update(dt_ms)
        self.bursts = [b for b in self.bursts if not b.done]
        self.pulse.update(dt_ms)
        self.timer_pulse.update(dt_ms)
        self.tongue.update_anim(dt_ms)
        self.icon_pulse.update(dt_ms)
        self.shake.update(dt_ms)
        if self._pop_in_ms is not None:
            self._pop_in_ms -= dt_ms
            if self._pop_in_ms <= 0:
                self._pop_in_ms = None
                self._emit(SoundEvent.PULSE_POP)

    def _update_playing(self, dt_ms: float) -> None:
        self._step_elapsed += dt_ms
        # o intervalo depende do tamanho e é recalculado a cada passo (FR-002/FR-003 da 004)
        while (
            self._step_elapsed >= self._interval()
            and self.game.status is Status.RUNNING
            and self.phase is Phase.PLAYING
            and not self._frenzy_cleared()
        ):
            self._step_elapsed -= self._interval()
            self._step_once()
        self._check_end()
        self.tongue.update_cooldown(dt_ms)  # a recarga só anda com a cobra andando (FR-011)
        self._announce_tongue_ready()
        self._update_frenzy(dt_ms)

    def _announce_tongue_ready(self) -> None:
        """Pulso + som quando a língua fica pronta; no Frenzy, espera o modo acabar (FR-005/009)."""
        if self._ready_announced or not self.tongue.ready or self.tongue_locked:
            return
        if self.phase is not Phase.PLAYING or self.game.status is not Status.RUNNING:
            return
        self._ready_announced = True
        self.icon_pulse.trigger()
        self._emit(SoundEvent.TONGUE_READY)

    def _interval(self) -> float:
        return step_interval_ms(len(self.game.snake), frenzy=self.game.in_frenzy)

    def _step_once(self) -> None:
        score_before = self.game.score
        specials_before = dict(self.game.specials)
        self.game.step()
        if self.game.status is Status.RUNNING:
            self._emit(SoundEvent.STEP)
        head = self.game.snake[0]
        if head in specials_before and head not in self.game.specials:
            # fruta especial: partículas da cor dela e som de coleta, sem pulso (FR-016 da 004)
            tint = SPECIAL_TINTS[specials_before[head]]
            self.bursts.append(ParticleBurst(head, self._fx_rng, tint=tint))
            self.shake.trigger(*EAT_SHAKE)
            self._emit(SoundEvent.EAT)
        if self.game.score > score_before:
            self._eat_effects(head)

    def _eat_effects(self, at) -> None:
        """Coleta de fruta normal (pelo passo ou pela língua): efeitos, sons e limiar do Frenzy."""
        self.bursts.append(ParticleBurst(at, self._fx_rng))
        self.pulse.trigger()
        self.shake.trigger(*EAT_SHAKE)
        self._emit(SoundEvent.EAT)
        self._pop_in_ms = PULSE_POP_DELAY_MS
        if self.game.score == threshold(self.frenzy_count):
            self._start_frenzy()

    # --- Feeding Frenzy (004) -------------------------------------------------------------

    def _frenzy_cleared(self) -> bool:
        return self.game.in_frenzy and not self.game.specials

    def _start_frenzy(self) -> None:
        if self.game.start_frenzy(SPECIAL_COUNT) == 0:
            return  # sem casa livre: o modo não começa
        self.frenzy_count += 1
        self.frenzy = Frenzy()
        self._impacts = 0
        self._emit(SoundEvent.MUSIC_STOP)
        self._go(Phase.FRENZY_INTRO)  # cobra e cronômetro parados durante a abertura

    def _update_intro(self) -> None:
        for i, start in enumerate(STAMP_DROP_AT):
            if self._impacts == i and self.phase_ms >= start + STAMP_DROP_MS:
                self._impact(i)
        if self.phase_ms >= INTRO_MS:
            self._go(Phase.PLAYING)
            self._emit(SoundEvent.MUSIC_FRENZY)

    def _impact(self, word: int) -> None:
        """A palavra bate: boom, tremor e detritos espalhados ao longo dela (FR-014)."""
        self._impacts += 1
        self._emit(SoundEvent.BOOM)
        self.shake.trigger(*STAMP_SHAKE)
        ox, oy = self.stamp_origins[word]
        angle = math.radians(STAMP_ANGLE_DEG)
        dx, dy = math.cos(angle), -math.sin(angle)
        for k in range(DEBRIS_BURSTS):
            along = STAMP_HALF_LENGTH * (2 * k / (DEBRIS_BURSTS - 1) - 1)
            origin = (ox + dx * along - 0.5, oy + dy * along - 0.5)  # -0,5: partículas são casas
            self.bursts.append(
                ParticleBurst(
                    origin,
                    self._fx_rng,
                    count=DEBRIS_COUNT,
                    speed=DEBRIS_SPEED,
                    life_ms=DEBRIS_LIFE_MS,
                    tint=SPECIAL_TINTS[word],
                )
            )

    def _update_frenzy(self, dt_ms: float) -> None:
        """Depois dos passos do quadro: comer a última especial vence o tempo esgotado."""
        if self.frenzy is None or self.phase is not Phase.PLAYING:
            return
        if self.game.status is not Status.RUNNING:
            return
        if self._frenzy_cleared():
            self._frenzy_survived()
            return
        for _second in self.frenzy.update(dt_ms):
            self._emit(SoundEvent.TIMER_TICK)
            self.timer_pulse.trigger()
        if self.frenzy.expired:
            self.game.fail()
            self._emit(SoundEvent.MUSIC_STOP)
            self._emit(SoundEvent.TIMEOUT_ALARM)
            self._go(Phase.TIMEOUT)

    def _frenzy_survived(self) -> None:
        """Comeu a última especial: partida para e "SURVIVED!" entra (FR-017)."""
        self.game.end_frenzy()
        self.frenzy = None
        self._emit(SoundEvent.MUSIC_STOP)
        self._go(Phase.SURVIVED)

    def _reset_round(self) -> None:
        """Partida nova: sem Frenzy e com a língua pronta."""
        self._reset_frenzy()
        self.tongue = Tongue()
        self._ready_announced = True

    def _reset_frenzy(self) -> None:
        self.frenzy = None
        self.frenzy_count = 0
        self.timer_pulse = ScorePulse()

    def _check_end(self) -> None:
        if self.phase is not Phase.PLAYING:
            return
        if self.game.status is Status.GAME_OVER:
            self.frenzy = None  # colisão no Frenzy: fim de jogo normal
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
        """Fim da partida: registra o resultado no placar (e salva) e abre o placar (005)."""
        self.frenzy = None
        self._emit(SoundEvent.LOSE if self.game.status is Status.GAME_OVER else SoundEvent.WIN)
        player = Entry(self.player_name or "?", self.game.score)
        before = list(self.highscores.entries)
        rank = self.highscores.insert(player.name, player.score)
        if self.highscores_path is not None:
            self.highscores.save(self.highscores_path)
        self.scoreboard = Scoreboard(before, list(self.highscores.entries), rank, player, self._fx_rng)
        self.menu = EndMenu()
        self._go(Phase.MENU_IN)

    def _update_scoreboard(self, dt_ms: float) -> None:
        self.scoreboard.update(dt_ms)
        for event in self.scoreboard.drain_events():
            self._emit(SCOREBOARD_SOUNDS[event])

    def _scoreboard_direction(self, direction: Direction) -> None:
        """Placar: ↑/↓ rolam, ←/→ escolhem a opção — só depois da animação (005/FR-009/010)."""
        if not self.scoreboard.done:
            return
        if direction in (Direction.UP, Direction.DOWN):
            moved = self.scoreboard.scroll(-1 if direction is Direction.UP else 1)
        else:
            moved = self.menu.move_up() if direction is Direction.LEFT else self.menu.move_down()
        if moved:
            self._emit(SoundEvent.NAV)

    def _leave_scoreboard(self, choice: MenuOption) -> None:
        self._end_choice = choice
        self._go(Phase.MENU_OUT)

    def _back_to_title(self) -> None:
        """Abandona a partida e volta ao começo (pausa -> "Tela inicial" e placar -> "Tela inicial")."""
        self.game.restart()
        self._reset_round()
        self.bursts = []
        self.pulse = ScorePulse()
        self.shake = ScreenShake(self._fx_rng)
        self._pop_in_ms = None
        self._enter_title()

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
        self._back_to_title()  # "Tela inicial"

    def _go(self, phase: Phase) -> None:
        self.phase = phase
        self.phase_ms = 0.0
        self._step_elapsed = 0.0

    def _emit(self, event: SoundEvent) -> None:
        self._sounds.append(event)
