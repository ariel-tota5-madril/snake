# Implementation Plan: Núcleo do Snake — movimento, comida e pontuação

**Branch**: `001-snake-core-gameplay` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-snake-core-gameplay/spec.md`

## Summary

Jogo Snake para um jogador: cobra controlada pelas setas em uma grade 20 × 20, comida gerada em
casa livre de forma reproduzível, pontuação de 1 ponto por comida e fim de partida ao bater na
parede ou no próprio corpo. A abordagem técnica separa um **núcleo puro** em Python (regras,
sem Pygame) de um **adaptador Pygame fino** (entrada, relógio e desenho), conforme o Princípio I
da constituição. O núcleo avança por passos discretos e recebe um `random.Random` injetado.

## Technical Context

**Language/Version**: Python 3.12 (código compatível com 3.12+; o `.venv` local usa 3.13)

**Primary Dependencies**: Pygame 2.6 (apenas no adaptador); biblioteca padrão no núcleo

**Storage**: N/A (sem persistência nesta feature)

**Testing**: pytest (apenas sobre o núcleo)

**Target Platform**: desktop (Linux, Windows, macOS) com janela gráfica

**Project Type**: desktop-app (jogo local)

**Performance Goals**: 8 passos de jogo por segundo; desenho a cada passo sem atraso perceptível

**Constraints**: núcleo sem Pygame, sem relógio e sem RNG global; determinístico por seed

**Scale/Scope**: grade 20 × 20; 1 jogador; ~3 módulos de código

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | Regras em `src/snake/core.py`, que não importa Pygame; `src/snake/app.py` só traduz teclas em `turn()`, chama `step()` no relógio e desenha o estado | ✅ |
| II. Test-first para regras | Cada regra (movimento, direção, comida, pontuação, colisão, vitória) entra por um teste em `tests/` que falha antes da implementação | ✅ |
| III. Simulação determinística | `Game` recebe um `random.Random` (ou seed); o tempo fica no adaptador; o núcleo avança por `step()` | ✅ |
| IV. Sem complexidade prematura | Um módulo de núcleo, um adaptador, um ponto de entrada; sem padrões, camadas ou configuração extra | ✅ |
| V. Jogável em todo checkpoint | Cada fase do `tasks.md` termina com `python -m snake` abrindo e `pytest` verde | ✅ |

**Re-check pós-design (Phase 1)**: o contrato em `contracts/core-api.md` expõe só `Game`,
`Direction` e `Status`, sem nenhum tipo do Pygame; o data model não depende de relógio. Gate
continua aprovado.

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
    └── app.py           # adaptador Pygame: teclado → turn(), relógio → step(), desenho

tests/
├── test_movement.py     # US1: movimento e direção
├── test_food.py         # US2: comida, crescimento e determinismo
├── test_score.py        # US3: pontuação
└── test_collision.py    # FR-011/012/013: game over, vitória, estado congelado

requirements.txt         # pygame, pytest
pyproject.toml           # configuração do pytest (pythonpath = src)
```

**Structure Decision**: projeto único com layout `src/`. O pacote `snake` contém o núcleo
(`core.py`) e o adaptador (`app.py`) em módulos separados; os testes importam apenas
`snake.core`.

## Complexity Tracking

Nenhuma violação da constituição; seção não aplicável.
