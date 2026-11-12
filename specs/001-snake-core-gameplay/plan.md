# Implementation Plan: Núcleo do Snake — movimento, comida e pontuação

**Branch**: `001-snake-core-gameplay` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-snake-core-gameplay/spec.md`

## Summary

Jogo Snake para um jogador: cobra controlada pelas setas em uma grade 20 × 20, comida gerada em
casa livre de forma reproduzível, pontuação de 1 ponto por comida, fim de partida ao bater na
parede ou no próprio corpo e menu de fim de partida ("Restart"/"Quit") navegado por ↑/↓ e
confirmado por Espaço/Enter. A abordagem técnica separa um **núcleo puro** em Python (regras,
sem Pygame) de um **adaptador Pygame fino** (entrada, relógio e desenho), conforme o Princípio I
da constituição. O núcleo avança por passos discretos e recebe um `random.Random` injetado. O
reinício é uma operação do núcleo (`Game.restart()`), e a seleção do menu é um pequeno módulo puro
(`menu.py`), também sem Pygame, para que toda decisão seja testável.

## Technical Context

**Language/Version**: Python 3.12 (código compatível com 3.12+; o `.venv` local usa 3.13)

**Primary Dependencies**: Pygame 2.6 (apenas no adaptador); biblioteca padrão no núcleo

**Storage**: N/A (sem persistência nesta feature)

**Testing**: pytest (apenas sobre o núcleo)

**Target Platform**: desktop (Linux, Windows, macOS) com janela gráfica

**Project Type**: desktop-app (jogo local)

**Performance Goals**: 8 passos de jogo por segundo; desenho a cada passo sem atraso perceptível

**Constraints**: núcleo sem Pygame, sem relógio e sem RNG global; determinístico por seed

**Scale/Scope**: grade 20 × 20; 1 jogador; ~4 módulos de código

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | Regras em `src/snake/core.py` e seleção do menu em `src/snake/menu.py`, ambos sem Pygame; `src/snake/app.py` só traduz teclas em `turn()`/ações do menu, chama `step()` no relógio e desenha o estado | ✅ |
| II. Test-first para regras | Cada regra (movimento, direção, comida, pontuação, colisão, vitória, reinício, menu) entra por um teste em `tests/` que falha antes da implementação | ✅ |
| III. Simulação determinística | `Game` recebe um `random.Random` (ou seed); o tempo fica no adaptador; o núcleo avança por `step()`; `restart()` reaproveita o mesmo RNG, então a sessão inteira é reproduzível | ✅ |
| IV. Sem complexidade prematura | Núcleo, menu (duas opções e um índice), adaptador e ponto de entrada; sem framework de telas nem máquina de estados genérica | ✅ |
| V. Jogável em todo checkpoint | Cada fase do `tasks.md` termina com `python -m snake` abrindo e `pytest` verde | ✅ |

**Re-check pós-design (Phase 1)**: o contrato em `contracts/core-api.md` expõe só `Game`,
`Direction`, `Status`, `EndMenu` e `MenuOption`, sem nenhum tipo do Pygame; o data model não
depende de relógio. Gate continua aprovado (revisado em 2026-11-12 após a clarificação do menu).

## Project Structure

### Documentation (this feature)

```text
specs/001-snake-core-gameplay/
├── plan.md              # Este arquivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── core-api.md      # Phase 1: interface pública do núcleo
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
└── snake/
    ├── __init__.py
    ├── __main__.py      # ponto de entrada: python -m snake
    ├── core.py          # núcleo puro: Game, Direction, Status (sem Pygame)
    ├── menu.py          # seleção do menu de fim de partida: EndMenu, MenuOption (sem Pygame)
    └── app.py           # adaptador Pygame: teclado → turn()/menu, relógio → step(), desenho

tests/
├── test_movement.py     # US1: movimento e direção
├── test_food.py         # US2: comida, crescimento e determinismo
├── test_score.py        # US3: pontuação
├── test_collision.py    # FR-011/012/013: game over, vitória, estado congelado
├── test_restart.py      # FR-014/015: reinício volta ao estado inicial com o mesmo RNG
├── test_menu.py         # FR-014/015: seleção e confirmação do menu
└── test_core_purity.py  # Princípio I/III: núcleo e menu sem Pygame nem relógio

requirements.txt         # -e . (instala o pacote e o pygame) + pytest
pyproject.toml           # projeto "snake" (dependência: pygame) + configuração do pytest
```

**Structure Decision**: projeto único com layout `src/`. O pacote `snake` contém o núcleo
(`core.py`), a lógica do menu (`menu.py`) e o adaptador (`app.py`) em módulos separados; os
testes importam apenas `snake.core` e `snake.menu`.

## Complexity Tracking

Nenhuma violação da constituição; seção não aplicável.
