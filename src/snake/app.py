"""Adaptador Pygame: traduz teclado em entradas do Flow, mede o tempo e desenha o estado.

Nenhuma regra de jogo nem regra de tela vive aqui (Princípio I da constituição).
"""

import math
from functools import cache
from pathlib import Path

import pygame

from snake import audio as audio_module
from snake.core import Direction, Status
from snake.flow import RESUME_STEP_MS, STAMP_ANGLE_DEG, UI_ANIM_MS, Flow, Phase, SoundEvent
from snake.juice import ease_out
from snake.menu import Menu, MenuOption
from snake.scoreboard import VISIBLE_ROWS

CELL = 48  # grade 30x30 -> janela 1440x1440 (FR-014)
S = CELL / 24  # escala da interface em relação ao tamanho original (24 px por casa)
FPS = 60
BACKGROUND = (20, 24, 32)
SNAKE_HEAD = (120, 220, 120)
SNAKE_BODY = (70, 170, 90)
FOOD = (230, 90, 70)
TEXT = (240, 240, 240)
DIM = (140, 140, 150)
HIGHLIGHT = (250, 210, 90)
FLASH_WHITE = (255, 255, 255)
FLASH_YELLOW = (255, 220, 60)
PARTICLE = (255, 170, 80)
OVERLAY_ALPHA = 170
TITLE_PHASES = {Phase.TITLE_IN, Phase.TITLE, Phase.TITLE_OUT}
MENU_PHASES = {Phase.MENU_IN, Phase.MENU, Phase.MENU_OUT}
PAUSE_UI = {Phase.PAUSE_IN, Phase.PAUSE, Phase.PAUSE_OUT}
OPTIONS_UI = {Phase.OPTIONS_IN, Phase.OPTIONS, Phase.OPTIONS_OUT}
SETTINGS_PATH = Path.home() / ".config" / "snake" / "settings.json"
HIGHSCORES_PATH = Path.home() / ".config" / "snake" / "highscores.json"
BOARD_W, BOARD_H = 300, 640  # painel vertical do placar (x S)
BOARD_TOP, ROW_H = 100, 64  # início da área das linhas e altura de cada linha (x S)
BOARD_BG = (28, 32, 44, 235)
SLIDER_BG = (60, 64, 76)
SPECIAL_COLORS = ((190, 90, 255), (255, 200, 40))  # 004: roxa ("FEEDING") e dourada ("FRENZY")
TINTS = {"fruit": PARTICLE, "purple": SPECIAL_COLORS[0], "gold": SPECIAL_COLORS[1]}
GLOW_PERIOD_MS = 1200
STAMP_WORDS = (("FEEDING", SPECIAL_COLORS[0]), ("FRENZY", (255, 225, 40)))  # roxo e amarelo
STAMP_OUTLINE = (15, 10, 25)
SURVIVED_COLOR = (110, 190, 255)  # azul claro
TIMER_COLOR = TEXT
TIMER_WARNING = (255, 70, 70)
QUIT_SOUND_WAIT_MS = 150  # deixa o som de confirmação do "Quit" tocar (≤ 0,3 s, US3 cenário 4)

KEYS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
}
WASD = {  # 005/FR-011: WASD vale como setas fora da entrada de nome
    pygame.K_w: Direction.UP,
    pygame.K_s: Direction.DOWN,
    pygame.K_a: Direction.LEFT,
    pygame.K_d: Direction.RIGHT,
}
NAME_UI = {Phase.NAME_IN, Phase.NAME, Phase.NAME_OUT}
CURSOR_BLINK_MS = 500
CONFIRM_KEYS = {pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER}


def draw_text(screen: pygame.Surface, font: pygame.font.Font, text: str, color, center) -> None:
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=center))


def draw_board(screen: pygame.Surface, flow: Flow) -> None:
    game = flow.game
    screen.fill(BACKGROUND)
    if game.food is not None:
        fx, fy = game.food
        pad = round(3 * S)
        pygame.draw.rect(screen, FOOD, (fx * CELL + pad, fy * CELL + pad, CELL - 2 * pad, CELL - 2 * pad))
    draw_specials(screen, flow)
    for i, (x, y) in enumerate(game.snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        gap = round(S)
        pygame.draw.rect(screen, color, (x * CELL + gap, y * CELL + gap, CELL - 2 * gap, CELL - 2 * gap))


@cache
def font_of(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, size)


@cache
def halo(color: tuple, alpha: int) -> pygame.Surface:
    """Brilho redondo em volta da fruta especial (cacheado por cor e intensidade)."""
    size = CELL * 2
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    for r, a in ((CELL * 0.95, alpha // 3), (CELL * 0.75, alpha // 2), (CELL * 0.55, alpha)):
        pygame.draw.circle(glow, (*color, a), (size / 2, size / 2), r)
    return glow


def draw_specials(screen: pygame.Surface, flow: Flow) -> None:
    """Frutas especiais roxas e douradas com brilho pulsando suavemente (FR-005 da 004)."""
    if not flow.game.specials:
        return
    wave = (1 + math.sin(2 * math.pi * pygame.time.get_ticks() / GLOW_PERIOD_MS)) / 2
    alpha = 40 + round(wave * 6) * 10  # degraus de 10: poucos brilhos diferentes no cache
    pad = round(3 * S)
    for (x, y), variant in flow.game.specials.items():
        color = SPECIAL_COLORS[variant]
        glow = halo(color, alpha)
        screen.blit(glow, glow.get_rect(center=((x + 0.5) * CELL, (y + 0.5) * CELL)))
        pygame.draw.rect(screen, color, (x * CELL + pad, y * CELL + pad, CELL - 2 * pad, CELL - 2 * pad))


@cache
def surface(size: tuple[int, int], alpha: bool) -> pygame.Surface:
    """Superfícies do tamanho da tela reaproveitadas entre quadros (criar 1440x1440 por quadro custa caro)."""
    return pygame.Surface(size, pygame.SRCALPHA) if alpha else pygame.Surface(size)


def blend(a, b, t: float):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw_particles(screen: pygame.Surface, flow: Flow) -> None:
    if not flow.bursts:
        return
    layer = surface(screen.get_size(), True)
    layer.fill((0, 0, 0, 0))
    for burst in flow.bursts:
        size = 9 * S if burst.life_ms > 600 else 4 * S  # detritos do carimbo são pedaços maiores
        for p in burst.particles:
            radius = max(1, round(size * p.life))
            center = ((p.x + 0.5) * CELL, (p.y + 0.5) * CELL)
            pygame.draw.circle(layer, (*TINTS[burst.tint], round(255 * p.life)), center, radius)
    screen.blit(layer, (0, 0))


def score_y(flow: Flow) -> float:
    """O placar fica escondido na tela inicial e entra deslizando de cima no começo da contagem."""
    if flow.phase in TITLE_PHASES or flow.phase in NAME_UI or (flow.phase in OPTIONS_UI and flow.options_origin is Phase.TITLE):
        return -30 * S
    if flow.phase is Phase.COUNTDOWN:
        return (-30 + 48 * ease_out(flow.phase_ms / UI_ANIM_MS)) * S
    return 18 * S


def draw_score(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    if flow.frenzy is not None:
        return  # no Frenzy (inclusive na abertura) o placar some e o cronômetro ocupa o topo (004)
    pulse = flow.pulse
    flash_color = blend(FLASH_WHITE, FLASH_YELLOW, pulse.warmth)
    label = font.render(f"Pontos: {flow.game.score}", True, blend(TEXT, flash_color, pulse.flash))
    if pulse.scale != 1:
        w, h = label.get_size()
        label = pygame.transform.smoothscale(label, (round(w * pulse.scale), round(h * pulse.scale)))
    rect = label.get_rect(midleft=(8 * S, score_y(flow)))
    if pulse.scale > 1 and rect.top < 4 * S:
        rect.top = round(4 * S)  # o pico do pulso (1,8x) não pode sair pela borda de cima
    screen.blit(label, rect)


def draw_timer(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    """Cronômetro grande no centro do topo e "N restantes" abaixo (FR-012/FR-019 da 004)."""
    if not flow.timer_visible:
        return
    cx = screen.get_width() / 2
    timer = flow.frenzy
    warning = timer.warning or flow.phase is Phase.TIMEOUT
    if flow.phase is not Phase.TIMEOUT or flow.timeout_blink:
        label = font_of(round(72 * S)).render(str(timer.seconds_left), True, TIMER_WARNING if warning else TIMER_COLOR)
        scale = flow.timer_pulse.scale if timer.warning else 1
        if scale != 1:
            w, h = label.get_size()
            label = pygame.transform.smoothscale(label, (round(w * scale), round(h * scale)))
        rect = label.get_rect(center=(cx, 34 * S))
        rect.top = max(rect.top, round(4 * S))  # o pulso não pode cortar o número na borda de cima
        screen.blit(label, rect)
    remaining = len(flow.game.specials)
    draw_text(screen, font, f"{remaining} restantes", TEXT, (cx, 72 * S))


@cache
def stamp_surface(word: str, color: tuple) -> pygame.Surface:
    """Palavra do carimbo com contorno escuro, já girada na diagonal (renderizada uma vez)."""
    return pygame.transform.rotozoom(stamp_label(word, color), STAMP_ANGLE_DEG, 1)


@cache
def stamp_label(word: str, color: tuple) -> pygame.Surface:
    """Palavra grande com contorno escuro, para ler sobre o tabuleiro."""
    font = font_of(round(84 * S))
    outline = round(4 * S)
    base = font.render(word, True, color)
    dark = font.render(word, True, STAMP_OUTLINE)
    w, h = base.get_size()
    canvas = pygame.Surface((w + 2 * outline, h + 2 * outline), pygame.SRCALPHA)
    for ox in (-outline, 0, outline):
        for oy in (-outline, 0, outline):
            canvas.blit(dark, (outline + ox, outline + oy))
    canvas.blit(base, (outline, outline))
    return canvas


def draw_stamps(screen: pygame.Surface, flow: Flow) -> None:
    """Abertura do Frenzy: "FEEDING" e "FRENZY" caindo de 4x até 1x (FR-013 da 004)."""
    alpha = round(255 * flow.stamp_alpha)
    dx, dy = flow.shake.offset
    for (word, color), scale, (x, y) in zip(STAMP_WORDS, flow.stamp_scales, flow.stamp_origins):
        if scale is None or alpha <= 0:
            continue
        label = stamp_surface(word, color)
        if scale != 1:
            w, h = label.get_size()
            label = pygame.transform.scale(label, (round(w * scale), round(h * scale)))
        else:
            label = label.copy()
        label.set_alpha(alpha)
        screen.blit(label, label.get_rect(center=((x + dx) * CELL, (y + dy) * CELL)))


def draw_survived(screen: pygame.Surface, flow: Flow) -> None:
    """ "SURVIVED!" azul entrando suave: aparece, cresce de 0,85x a 1x e sobe um pouco (FR-017)."""
    progress = flow.survived_progress
    if progress <= 0:
        return
    label = stamp_label("SURVIVED!", SURVIVED_COLOR)
    scale = 0.85 + 0.15 * progress
    w, h = label.get_size()
    label = pygame.transform.smoothscale(label, (round(w * scale), round(h * scale)))
    label.set_alpha(round(255 * progress))
    cx, cy = screen.get_rect().center
    screen.blit(label, label.get_rect(center=(cx, cy + (1 - progress) * CELL / 2)))


def draw_panel(screen: pygame.Surface, panel: pygame.Surface, progress: float) -> None:
    """Escurece o fundo e mostra o painel crescendo de 80% a 100% e surgindo conforme progress."""
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, round(OVERLAY_ALPHA * progress)))
    screen.blit(shade, (0, 0))
    if progress <= 0:
        return
    if progress >= 1:
        screen.blit(panel, panel.get_rect(center=screen.get_rect().center))
        return
    scale = 0.8 + 0.2 * progress
    w, h = panel.get_size()
    scaled = pygame.transform.smoothscale(panel, (max(1, round(w * scale)), max(1, round(h * scale))))
    scaled.set_alpha(round(255 * progress))
    screen.blit(scaled, scaled.get_rect(center=screen.get_rect().center))


def lines_panel(font: pygame.font.Font, lines: list[tuple[str, tuple]], size) -> pygame.Surface:
    panel = pygame.Surface(size, pygame.SRCALPHA)
    cx = size[0] / 2
    for i, (text, color) in enumerate(lines):
        draw_text(panel, font, text, color, (cx, (20 + i * 36) * S))
    return panel


def menu_lines(menu: Menu) -> list[tuple[str, tuple]]:
    lines = []
    for option in menu.options:
        selected = option is menu.selected
        lines.append((f"> {option.value} <" if selected else option.value, HIGHLIGHT if selected else DIM))
    return lines


def draw_title(screen: pygame.Surface, big: pygame.font.Font, font: pygame.font.Font, flow: Flow) -> None:
    panel = pygame.Surface((round(420 * S), round(240 * S)), pygame.SRCALPHA)  # 3 opções (005)
    draw_text(panel, big, "Snake", SNAKE_HEAD, (210 * S, 45 * S))
    for i, (text, color) in enumerate(menu_lines(flow.title_menu)):
        draw_text(panel, font, text, color, (210 * S, (120 + i * 36) * S))
    draw_panel(screen, panel, flow.ui_progress)


def draw_pause(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    lines = [("Pausado", TEXT), ("", TEXT)] + menu_lines(flow.pause_menu)
    draw_panel(screen, lines_panel(font, lines, (round(360 * S), round(180 * S))), flow.ui_progress)


def draw_options(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    """Tela de Opções: "Música" e "Efeitos" com barras de 10 segmentos, e "Voltar"."""
    width, row = round(420 * S), 44 * S
    panel = pygame.Surface((width, round(230 * S)), pygame.SRCALPHA)
    draw_text(panel, font, "Opções", TEXT, (width / 2, 20 * S))
    values = {MenuOption.MUSIC: flow.settings.music, MenuOption.SFX: flow.settings.sfx}
    for i, option in enumerate(flow.options_menu.options):
        y = 70 * S + i * row
        selected = option is flow.options_menu.selected
        color = HIGHLIGHT if selected else DIM
        if option not in values:
            draw_text(panel, font, f"> {option.value} <" if selected else option.value, color, (width / 2, y))
            continue
        label = font.render(("> " if selected else "") + option.value, True, color)
        panel.blit(label, label.get_rect(midleft=(16 * S, y)))
        segments = values[option] // 10
        for k in range(10):
            rect = pygame.Rect(round(190 * S + k * 16 * S), round(y - 9 * S), round(12 * S), round(18 * S))
            pygame.draw.rect(panel, color if k < segments else SLIDER_BG, rect)
        pct = font.render(f"{values[option]}%", True, color)
        panel.blit(pct, pct.get_rect(midleft=(360 * S, y)))
    draw_panel(screen, panel, flow.ui_progress)


def draw_big_number(screen: pygame.Surface, big: pygame.font.Font, number: int, within: float) -> None:
    """Número de contagem que surge grande e encolhe; within vai de 0 a 1 em cada número."""
    label = big.render(str(number), True, HIGHLIGHT)
    scale = 1.6 - 0.6 * ease_out(within)
    w, h = label.get_size()
    label = pygame.transform.smoothscale(label, (round(w * scale), round(h * scale)))
    label.set_alpha(round(255 * (1 - 0.5 * within)))
    screen.blit(label, label.get_rect(center=screen.get_rect().center))


def draw_countdown(screen: pygame.Surface, big: pygame.font.Font, flow: Flow) -> None:
    draw_big_number(screen, big, flow.countdown_number, (flow.phase_ms % 1000) / 1000)


def draw_resume(screen: pygame.Surface, big: pygame.font.Font, flow: Flow) -> None:
    within = (flow.phase_ms % RESUME_STEP_MS) / RESUME_STEP_MS
    draw_big_number(screen, big, flow.resume_number, within)


def draw_name_entry(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    """Painel do nome do jogador (005/US1) com cursor piscando."""
    width, height = round(420 * S), round(180 * S)
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    draw_text(panel, font, "Seu nome", TEXT, (width / 2, 24 * S))
    field = pygame.Rect(round(40 * S), round(56 * S), width - round(80 * S), round(48 * S))
    pygame.draw.rect(panel, SLIDER_BG, field, border_radius=round(6 * S))
    text = flow.name_entry.text if flow.name_entry else ""
    cursor = "_" if (pygame.time.get_ticks() // CURSOR_BLINK_MS) % 2 == 0 else " "
    draw_text(panel, font, text + cursor, HIGHLIGHT, field.center)
    draw_text(panel, font, "Enter para jogar  ·  Esc volta", DIM, (width / 2, 140 * S))
    draw_panel(screen, panel, flow.ui_progress)


@cache
def glyph(ch: str, color: tuple) -> pygame.Surface:
    return font_of(round(36 * S)).render(ch, True, color)


def draw_chars(panel, text: str, color, x: float, y: float, offsets=None, align_right=False) -> None:
    """Texto desenhado letra a letra (com o espaçamento normal da fonte): cada letra pode voar."""
    glyphs = [glyph(ch, color) for ch in text]
    start = x - sum(g.get_width() for g in glyphs) if align_right else x
    for i, g in enumerate(glyphs):
        dx, dy = offsets[i] if offsets else (0, 0)
        panel.blit(g, g.get_rect(midleft=(start + dx * ROW_H * S, y + dy * ROW_H * S)))
        start += g.get_width()


def draw_arrow(panel, center, up: bool) -> None:
    x, y = center
    h = 8 * S
    tip, base = (y - h, y + h) if up else (y + h, y - h)
    pygame.draw.polygon(panel, DIM, [(x, tip), (x - 12 * S, base), (x + 12 * S, base)])


def draw_entry(panel, entry, color, y: float, offsets=None) -> None:
    name_offsets = offsets[: len(entry.name)] if offsets else None
    score_offsets = offsets[len(entry.name) :] if offsets else None
    draw_chars(panel, entry.name, color, 64 * S, y, name_offsets)
    draw_chars(panel, str(entry.score), color, (BOARD_W - 18) * S, y, score_offsets, align_right=True)


def draw_scoreboard(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    """Placar vertical (005): 5 linhas visíveis com rolagem, resultado de fora e opções."""
    board = flow.scoreboard
    width, height = round(BOARD_W * S), round(BOARD_H * S)
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel, BOARD_BG, panel.get_rect(), border_radius=round(10 * S))
    title = "Game Over" if flow.game.status is Status.GAME_OVER else "Você venceu!"
    draw_text(panel, font, title, DIM, (width / 2, 24 * S))
    draw_text(panel, font_of(round(52 * S)), "HIGHSCORES", HIGHLIGHT, (width / 2, 62 * S))
    top, row_h = BOARD_TOP * S, ROW_H * S
    area = pygame.Rect(0, round(top), width, round(VISIBLE_ROWS * row_h))
    panel.set_clip(area)
    view = board.view_top
    for i in range(len(board.after)):  # números das posições acompanham as linhas
        draw_text(panel, font, f"{i + 1}.", DIM, (34 * S, top + (i - view + 0.5) * row_h))
    for row in board.rows():
        color = HIGHLIGHT if row.is_player else TEXT
        draw_entry(panel, row.entry, color, top + (row.y - view + 0.5) * row_h)
    panel.set_clip(None)
    if view > 0.01:
        draw_arrow(panel, (width / 2, top - 10 * S), up=True)
    if view < max(0, len(board.after) - VISIBLE_ROWS) - 0.01:
        draw_arrow(panel, (width / 2, area.bottom + 12 * S), up=False)
    if board.outside is not None:
        draw_text(panel, font, "Seu resultado", DIM, (width / 2, area.bottom + 40 * S))
        draw_entry(panel, board.outside, HIGHLIGHT, area.bottom + 74 * S)
    if board.done:
        small = font_of(round(28 * S))
        for i, option in enumerate(flow.menu.options):  # lado a lado, escolhidas com ←/→
            selected = option is flow.menu.selected
            center = (width * (0.27 + 0.46 * i), height - 44 * S)
            draw_text(panel, small, option.value, HIGHLIGHT if selected else DIM, center)
            if selected:
                bar = pygame.Rect(0, 0, round(120 * S), round(3 * S))
                bar.center = (center[0], center[1] + 18 * S)
                pygame.draw.rect(panel, HIGHLIGHT, bar)
    draw_panel(screen, panel, flow.ui_progress)


def draw_end_menu(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    draw_scoreboard(screen, font, flow)


def draw(screen: pygame.Surface, fonts: tuple[pygame.font.Font, pygame.font.Font], flow: Flow) -> None:
    font, big = fonts
    world = surface(screen.get_size(), False)
    draw_board(world, flow)
    draw_particles(world, flow)
    screen.fill(BACKGROUND)
    dx, dy = flow.shake.offset  # em casas
    screen.blit(world, (dx * CELL, dy * CELL))
    draw_score(screen, font, flow)
    draw_timer(screen, font, flow)
    if flow.phase is Phase.FRENZY_INTRO:
        draw_stamps(screen, flow)
    elif flow.phase is Phase.SURVIVED:
        draw_survived(screen, flow)
    if flow.phase in TITLE_PHASES:
        draw_title(screen, big, font, flow)
    elif flow.phase in NAME_UI:
        draw_name_entry(screen, font, flow)
    elif flow.phase is Phase.COUNTDOWN:
        draw_countdown(screen, big, flow)
    elif flow.phase in MENU_PHASES and flow.menu is not None:
        draw_end_menu(screen, font, flow)
    elif flow.phase in PAUSE_UI:
        draw_pause(screen, font, flow)
    elif flow.phase is Phase.RESUME:
        draw_resume(screen, big, flow)
    elif flow.phase in OPTIONS_UI:
        draw_options(screen, font, flow)
    pygame.display.flip()


def handle_event(flow: Flow, event: pygame.event.Event) -> None:
    if event.type == pygame.QUIT:
        flow.quit()
    elif event.type == pygame.KEYDOWN and flow.accepts_text:
        # entrada de nome: letras são texto; Enter, Esc e Backspace são comandos
        if event.key in CONFIRM_KEYS and event.key != pygame.K_SPACE:
            flow.confirm()
        elif event.key == pygame.K_ESCAPE:
            flow.escape()
        elif event.key == pygame.K_BACKSPACE:
            flow.backspace()
        elif event.unicode:
            flow.type_text(event.unicode)
    elif event.type == pygame.KEYDOWN:
        if event.key in WASD:
            flow.direction(WASD[event.key])
        elif event.key in KEYS:
            flow.direction(KEYS[event.key])
        elif event.key in CONFIRM_KEYS:
            flow.confirm()
        elif event.key == pygame.K_ESCAPE:
            flow.escape()


def run() -> None:
    audio_module.pre_init()
    pygame.init()
    flow = Flow(settings_path=SETTINGS_PATH, highscores_path=HIGHSCORES_PATH)
    audio = audio_module.Audio.create(flow.settings)
    screen = pygame.display.set_mode((flow.game.width * CELL, flow.game.height * CELL))
    pygame.display.set_caption("Snake")
    fonts = (pygame.font.Font(None, round(36 * S)), pygame.font.Font(None, round(96 * S)))
    clock = pygame.time.Clock()
    last_sounds: list[SoundEvent] = []
    while not flow.quit_requested:
        for event in pygame.event.get():
            handle_event(flow, event)
        flow.update(clock.tick(FPS))
        audio.apply_volumes(flow.settings)  # mudanças de volume valem na hora (FR-018)
        last_sounds = flow.drain_sounds()
        for sound in last_sounds:
            audio.play(sound)
        draw(screen, fonts, flow)
    remaining = flow.drain_sounds()  # eventos gerados depois do último desenho
    for sound in remaining:
        audio.play(sound)
    if SoundEvent.CONFIRM in last_sounds + remaining:
        pygame.time.wait(QUIT_SOUND_WAIT_MS)
    pygame.quit()
