# Snake

Jogo Snake em Python, construído com Spec-Driven Development (GitHub Spec Kit).
Especificações, planos e tarefas por feature em [`specs/`](specs/)
(001: núcleo do jogo; 002: game juice);
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

Fluxo de telas: **tela inicial** (Espaço/Enter para começar) → **contagem 3, 2, 1** →
**partida** → ao bater, a tela treme → **menu de fim** com "Restart" e "Quit".

- Setas: mudam a direção da cobra; no menu, ↑/↓ escolhem a opção.
- Espaço ou Enter: começam o jogo na tela inicial e confirmam a opção do menu.
- "Restart" volta direto para a contagem; "Quit" fecha o jogo.

## Estrutura

- `src/snake/core.py` — núcleo puro: todas as regras, sem Pygame, sem relógio, RNG injetado.
- `src/snake/menu.py` — seleção do menu de fim de partida (sem Pygame).
- `src/snake/juice.py` — efeitos: partículas, pulso do placar, tremor (sem Pygame nem relógio).
- `src/snake/flow.py` — fases de tela e relógio de passos; recebe o tempo de fora (sem Pygame).
- `src/snake/app.py` — adaptador Pygame: teclado e relógio → `Flow`, desenho.
- `tests/` — testes das regras e das telas, todos sem abrir janela.
