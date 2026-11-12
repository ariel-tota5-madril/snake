"""Adaptador Pygame: traduz teclado em comandos, o relógio em passos e desenha o estado.

Nenhuma regra de jogo vive aqui (Princípio I da constituição).
"""

import pygame

from snake.core import Direction, Game, Status

CELL = 24
STEPS_PER_SECOND = 8
FPS = 60
BACKGROUND = (20, 24, 32)
SNAKE_HEAD = (120, 220, 120)
SNAKE_BODY = (70, 170, 90)
FOOD = (230, 90, 70)
TEXT = (240, 240, 240)

KEYS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
}


def draw_centered(screen: pygame.Surface, font: pygame.font.Font, text: str) -> None:
    label = font.render(text, True, TEXT)
    screen.blit(label, label.get_rect(center=screen.get_rect().center))


def draw(screen: pygame.Surface, font: pygame.font.Font, game: Game) -> None:
    screen.fill(BACKGROUND)
    if game.food is not None:
        fx, fy = game.food
        pygame.draw.rect(screen, FOOD, (fx * CELL + 3, fy * CELL + 3, CELL - 6, CELL - 6))
    for i, (x, y) in enumerate(game.snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        pygame.draw.rect(screen, color, (x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2))
    score = font.render(f"Pontos: {game.score}", True, TEXT)
    screen.blit(score, (8, 6))
    if game.status is Status.GAME_OVER:
        draw_centered(screen, font, f"Game Over - {game.score} pontos")
    elif game.status is Status.WON:
        draw_centered(screen, font, f"Você venceu! - {game.score} pontos")
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
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in KEYS:
                game.turn(KEYS[event.key])
        elapsed += clock.tick(FPS)
        while elapsed >= step_interval:
            game.step()
            elapsed -= step_interval
        draw(screen, font, game)
    pygame.quit()
