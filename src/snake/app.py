"""Adaptador Pygame: traduz teclado em entradas do Flow, mede o tempo e desenha o estado.

Nenhuma regra de jogo nem regra de tela vive aqui (Princípio I da constituição).
"""

from functools import cache

import pygame

from snake.core import Direction, Status
from snake.flow import UI_ANIM_MS, Flow, Phase
from snake.juice import ease_out

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

KEYS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
}
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
    for i, (x, y) in enumerate(game.snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        gap = round(S)
        pygame.draw.rect(screen, color, (x * CELL + gap, y * CELL + gap, CELL - 2 * gap, CELL - 2 * gap))


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
        for p in burst.particles:
            radius = max(1, round(4 * S * p.life))
            center = ((p.x + 0.5) * CELL, (p.y + 0.5) * CELL)
            pygame.draw.circle(layer, (*PARTICLE, round(255 * p.life)), center, radius)
    screen.blit(layer, (0, 0))


def score_y(flow: Flow) -> float:
    """O placar fica escondido na tela inicial e entra deslizando de cima no começo da contagem."""
    if flow.phase in TITLE_PHASES:
        return -30 * S
    if flow.phase is Phase.COUNTDOWN:
        return (-30 + 48 * ease_out(flow.phase_ms / UI_ANIM_MS)) * S
    return 18 * S


def draw_score(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    pulse = flow.pulse
    flash_color = blend(FLASH_WHITE, FLASH_YELLOW, pulse.warmth)
    label = font.render(f"Pontos: {flow.game.score}", True, blend(TEXT, flash_color, pulse.flash))
    if pulse.scale != 1:
        w, h = label.get_size()
        label = pygame.transform.smoothscale(label, (round(w * pulse.scale), round(h * pulse.scale)))
    rect = label.get_rect(midleft=(8 * S, score_y(flow)))
    if flow.phase not in TITLE_PHASES and rect.top < 4 * S:
        rect.top = round(4 * S)  # o pico do pulso (1,8x) não pode sair pela borda de cima
    screen.blit(label, rect)


def draw_panel(screen: pygame.Surface, panel: pygame.Surface, progress: float) -> None:
    """Escurece o fundo e mostra o painel crescendo de 80% a 100% e surgindo conforme progress."""
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, round(OVERLAY_ALPHA * progress)))
    screen.blit(shade, (0, 0))
    if progress <= 0:
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


def draw_title(screen: pygame.Surface, big: pygame.font.Font, font: pygame.font.Font, flow: Flow) -> None:
    panel = pygame.Surface((round(420 * S), round(140 * S)), pygame.SRCALPHA)
    draw_text(panel, big, "Snake", SNAKE_HEAD, (210 * S, 45 * S))
    draw_text(panel, font, "Pressione Espaço para começar", TEXT, (210 * S, 110 * S))
    draw_panel(screen, panel, flow.ui_progress)


def draw_countdown(screen: pygame.Surface, big: pygame.font.Font, flow: Flow) -> None:
    within = (flow.phase_ms % 1000) / 1000  # cada número surge grande e encolhe
    label = big.render(str(flow.countdown_number), True, HIGHLIGHT)
    scale = 1.6 - 0.6 * ease_out(within)
    w, h = label.get_size()
    label = pygame.transform.smoothscale(label, (round(w * scale), round(h * scale)))
    label.set_alpha(round(255 * (1 - 0.5 * within)))
    screen.blit(label, label.get_rect(center=screen.get_rect().center))


def draw_end_menu(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    title = "Game Over" if flow.game.status is Status.GAME_OVER else "Você venceu!"
    lines = [(title, TEXT), (f"Pontuação final: {flow.game.score}", TEXT), ("", TEXT)]
    for option in flow.menu.options:
        selected = option is flow.menu.selected
        label = f"> {option.value} <" if selected else option.value
        lines.append((label, HIGHLIGHT if selected else DIM))
    draw_panel(screen, lines_panel(font, lines, (round(360 * S), round(180 * S))), flow.ui_progress)


def draw(screen: pygame.Surface, fonts: tuple[pygame.font.Font, pygame.font.Font], flow: Flow) -> None:
    font, big = fonts
    world = surface(screen.get_size(), False)
    draw_board(world, flow)
    draw_particles(world, flow)
    screen.fill(BACKGROUND)
    dx, dy = flow.shake.offset  # em casas
    screen.blit(world, (dx * CELL, dy * CELL))
    draw_score(screen, font, flow)
    if flow.phase in TITLE_PHASES:
        draw_title(screen, big, font, flow)
    elif flow.phase is Phase.COUNTDOWN:
        draw_countdown(screen, big, flow)
    elif flow.phase in MENU_PHASES and flow.menu is not None:
        draw_end_menu(screen, font, flow)
    pygame.display.flip()


def handle_event(flow: Flow, event: pygame.event.Event) -> None:
    if event.type == pygame.QUIT:
        flow.quit()
    elif event.type == pygame.KEYDOWN:
        if event.key in KEYS:
            flow.direction(KEYS[event.key])
        elif event.key in CONFIRM_KEYS:
            flow.confirm()


def run() -> None:
    pygame.init()
    flow = Flow()
    screen = pygame.display.set_mode((flow.game.width * CELL, flow.game.height * CELL))
    pygame.display.set_caption("Snake")
    fonts = (pygame.font.Font(None, round(36 * S)), pygame.font.Font(None, round(96 * S)))
    clock = pygame.time.Clock()
    while not flow.quit_requested:
        for event in pygame.event.get():
            handle_event(flow, event)
        flow.update(clock.tick(FPS))
        draw(screen, fonts, flow)
    pygame.quit()
