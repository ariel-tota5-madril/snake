# Snake

Jogo Snake em Python, construído com Spec-Driven Development (GitHub Spec Kit).
Especificação, plano e tarefas em [`specs/001-snake-core-gameplay/`](specs/001-snake-core-gameplay/);
regras do projeto em [`.specify/memory/constitution.md`](.specify/memory/constitution.md).

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Testes

```bash
pytest
```

## Jogar

```bash
python -m snake
```

Setas mudam a direção. A partida termina ao bater na parede ou no próprio corpo.

## Estrutura

- `src/snake/core.py` — núcleo puro: todas as regras, sem Pygame, sem relógio, RNG injetado.
- `src/snake/app.py` — adaptador Pygame: teclado → `turn()`, relógio → `step()`, desenho.
- `tests/` — testes das regras (apenas sobre o núcleo).
