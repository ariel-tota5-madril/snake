"""Adaptador Pygame: traduz teclado em entradas do Flow, mede o tempo e desenha o estado.

Nenhuma regra de jogo nem regra de tela vive aqui (Princípio I da constituição).
"""

import pygame

from snake.core import Direction, Status
from snake.flow import UI_ANIM_MS, Flow, Phase
from snake.juice import ease_out

CELL = 24
FPS = 60
BACKGROUND = (20, 24, 32)
SNAKE_HEAD = (120, 220, 120)
SNAKE_BODY = (70, 170, 90)
FOOD = (230, 90, 70)
TEXT = (240, 240, 240)
DIM = (140, 140, 150)
HIGHLIGHT = (250, 210, 90)
FLASH = (255, 220, 60)
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
        pygame.draw.rect(screen, FOOD, (fx * CELL + 3, fy * CELL + 3, CELL - 6, CELL - 6))
    for i, (x, y) in enumerate(game.snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        pygame.draw.rect(screen, color, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2))


def blend(a, b, t: float):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw_particles(screen: pygame.Surface, flow: Flow) -> None:
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for burst in flow.bursts:
        for p in burst.particles:
            radius = max(1, round(4 * p.life))
            center = ((p.x + 0.5) * CELL, (p.y + 0.5) * CELL)
            pygame.draw.circle(layer, (*PARTICLE, round(255 * p.life)), center, radius)
    screen.blit(layer, (0, 0))


def score_y(flow: Flow) -> float:
    """O placar fica escondido na tela inicial e entra deslizando de cima no começo da contagem."""
    if flow.phase in TITLE_PHASES:
        return -30
    if flow.phase is Phase.COUNTDOWN:
        return -30 + 48 * ease_out(flow.phase_ms / UI_ANIM_MS)
    return 18


def draw_score(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    pulse = flow.pulse
    label = font.render(f"Pontos: {flow.game.score}", True, blend(TEXT, FLASH, pulse.flash))
    if pulse.scale != 1:
        w, h = label.get_size()
        label = pygame.transform.smoothscale(label, (round(w * pulse.scale), round(h * pulse.scale)))
    screen.blit(label, label.get_rect(midleft=(8, score_y(flow))))


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
        draw_text(panel, font, text, color, (cx, 20 + i * 36))
    return panel


def draw_title(screen: pygame.Surface, big: pygame.font.Font, font: pygame.font.Font, flow: Flow) -> None:
    panel = pygame.Surface((420, 140), pygame.SRCALPHA)
    draw_text(panel, big, "Snake", SNAKE_HEAD, (210, 45))
    draw_text(panel, font, "Pressione Espaço para começar", TEXT, (210, 110))
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
    draw_panel(screen, lines_panel(font, lines, (360, 180)), flow.ui_progress)


def draw(screen: pygame.Surface, fonts: tuple[pygame.font.Font, pygame.font.Font], flow: Flow) -> None:
    font, big = fonts
    world = pygame.Surface(screen.get_size())
    draw_board(world, flow)
    draw_particles(world, flow)
    screen.fill(BACKGROUND)
    screen.blit(world, flow.shake.offset)
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
    fonts = (pygame.font.Font(None, 36), pygame.font.Font(None, 96))
    clock = pygame.time.Clock()
    while not flow.quit_requested:
        for event in pygame.event.get():
            handle_event(flow, event)
        flow.update(clock.tick(FPS))
        draw(screen, fonts, flow)
    pygame.quit()
