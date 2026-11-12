"""Adaptador Pygame: traduz teclado em comandos, o relógio em passos e desenha o estado.

Nenhuma regra de jogo vive aqui (Princípio I da constituição).
"""

import pygame

from snake.core import Direction, Game, Status
from snake.menu import EndMenu, MenuOption

CELL = 24
STEPS_PER_SECOND = 8
FPS = 60
BACKGROUND = (20, 24, 32)
SNAKE_HEAD = (120, 220, 120)
SNAKE_BODY = (70, 170, 90)
FOOD = (230, 90, 70)
TEXT = (240, 240, 240)
DIM = (140, 140, 150)
HIGHLIGHT = (250, 210, 90)
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


def draw_end_menu(screen: pygame.Surface, font: pygame.font.Font, game: Game, menu: EndMenu) -> None:
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill(OVERLAY)
    screen.blit(shade, (0, 0))
    cx, cy = screen.get_rect().center
    title = "Game Over" if game.status is Status.GAME_OVER else "Você venceu!"
    draw_text(screen, font, title, TEXT, (cx, cy - 70))
    draw_text(screen, font, f"Pontuação final: {game.score}", TEXT, (cx, cy - 35))
    for i, option in enumerate(menu.options):
        selected = option is menu.selected
        label = f"> {option.value} <" if selected else option.value
        draw_text(screen, font, label, HIGHLIGHT if selected else DIM, (cx, cy + 15 + i * 36))


def draw(screen: pygame.Surface, font: pygame.font.Font, game: Game, menu: EndMenu | None) -> None:
    screen.fill(BACKGROUND)
    if game.food is not None:
        fx, fy = game.food
        pygame.draw.rect(screen, FOOD, (fx * CELL + 3, fy * CELL + 3, CELL - 6, CELL - 6))
    for i, (x, y) in enumerate(game.snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        pygame.draw.rect(screen, color, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2))
    score = font.render(f"Pontos: {game.score}", True, TEXT)
    screen.blit(score, (8, 6))
    if menu is not None:
        draw_end_menu(screen, font, game, menu)
    pygame.display.flip()


def run() -> None:
    pygame.init()
    game = Game()
    screen = pygame.display.set_mode((game.width * CELL, game.height * CELL))
    pygame.display.set_caption("Snake")
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    step_interval = 1000 / STEPS_PER_SECOND
    elapsed = 0.0
    menu: EndMenu | None = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type != pygame.KEYDOWN:
                continue
            elif menu is None:
                if event.key in KEYS:
                    game.turn(KEYS[event.key])
                # Espaço/Enter durante a partida não fazem nada (FR-016)
            elif event.key == pygame.K_UP:
                menu.move_up()
            elif event.key == pygame.K_DOWN:
                menu.move_down()
            elif event.key in CONFIRM_KEYS:
                if menu.confirm() is MenuOption.RESTART:
                    game.restart()
                    menu = None
                    elapsed = 0.0
                else:
                    running = False
        if menu is None:
            elapsed += clock.tick(FPS)
            while elapsed >= step_interval and game.status is Status.RUNNING:
                game.step()
                elapsed -= step_interval
            if game.status is not Status.RUNNING:
                menu = EndMenu()
        else:
            clock.tick(FPS)
        draw(screen, font, game, menu)
    pygame.quit()
