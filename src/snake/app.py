"""Adaptador Pygame: traduz teclado em entradas do Flow, mede o tempo e desenha o estado.

Nenhuma regra de jogo nem regra de tela vive aqui (Princípio I da constituição).
"""

import pygame

from snake.core import Direction, Status
from snake.flow import Flow
from snake.menu import EndMenu

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
OVERLAY = (0, 0, 0, 170)

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


def draw_score(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    pulse = flow.pulse
    label = font.render(f"Pontos: {flow.game.score}", True, blend(TEXT, FLASH, pulse.flash))
    if pulse.scale != 1:
        w, h = label.get_size()
        label = pygame.transform.smoothscale(label, (round(w * pulse.scale), round(h * pulse.scale)))
    screen.blit(label, label.get_rect(midleft=(8, 18)))


def draw_end_menu(screen: pygame.Surface, font: pygame.font.Font, flow: Flow, menu: EndMenu) -> None:
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill(OVERLAY)
    screen.blit(shade, (0, 0))
    cx, cy = screen.get_rect().center
    title = "Game Over" if flow.game.status is Status.GAME_OVER else "Você venceu!"
    draw_text(screen, font, title, TEXT, (cx, cy - 70))
    draw_text(screen, font, f"Pontuação final: {flow.game.score}", TEXT, (cx, cy - 35))
    for i, option in enumerate(menu.options):
        selected = option is menu.selected
        label = f"> {option.value} <" if selected else option.value
        draw_text(screen, font, label, HIGHLIGHT if selected else DIM, (cx, cy + 15 + i * 36))


def draw(screen: pygame.Surface, font: pygame.font.Font, flow: Flow) -> None:
    draw_board(screen, flow)
    draw_particles(screen, flow)
    draw_score(screen, font, flow)
    if flow.menu is not None:
        draw_end_menu(screen, font, flow, flow.menu)
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
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    while not flow.quit_requested:
        for event in pygame.event.get():
            handle_event(flow, event)
        flow.update(clock.tick(FPS))
        draw(screen, font, flow)
    pygame.quit()
