# Implementation Plan: Game juice — feedback visual do Snake

**Branch**: `002-game-juice` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-game-juice/spec.md`

## Summary

Adicionar feedback visual ao Snake: partículas na cabeça, pulso "punchy" com flash de cor no
placar e mini tremor ao comer, tremor de tela na colisão, grade 30×30 em janela 1440×1440, tela inicial animada, contagem regressiva "3, 2, 1" antes de
toda partida e animações de entrada/saída da janela de fim de partida. Abordagem: toda decisão de
tempo e de fase vira **lógica pura testável** — um módulo de efeitos (`juice.py`) e um fluxo de
telas (`flow.py`) que avançam por `update(dt_ms)` recebido de fora, com RNG próprio semeado. O
adaptador Pygame (`app.py`) só lê o relógio e o teclado, repassa ao fluxo e desenha o que o fluxo
expõe. O núcleo de regras (`core.py`) não muda: a grade 30×30 é passada pelo `Flow` ao criar o
`Game` (o padrão 20×20 do núcleo e seus testes continuam valendo).

## Technical Context

**Language/Version**: Python 3.12 (compatível com 3.12+; `.venv` local em 3.13), igual à 001

**Primary Dependencies**: Pygame 2.6 (apenas no adaptador); biblioteca padrão nos módulos puros

**Storage**: N/A

**Testing**: pytest, sobre `core`, `menu`, `juice` e `flow` (sem janela)

**Target Platform**: desktop com janela gráfica

**Project Type**: desktop-app (jogo local)

**Performance Goals**: 60 quadros por segundo com até 3 explosões de partículas simultâneas
(SC-004) na janela de 1440×1440; 8 passos de jogo por segundo (inalterado)

**Constraints**: efeitos não alteram o estado do jogo (FR-010); efeitos determinísticos por seed
sem mexer na sequência de comidas da 001 (FR-011, SC-005); nenhum módulo puro lê relógio

**Scale/Scope**: 2 módulos puros novos, adaptador reescrito, ~2 arquivos de teste novos; grade
30×30 (casas de 48 px)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | `core.py` intocado (tamanho da grade é parâmetro que já existe). Efeitos (`juice.py`) e fases de tela (`flow.py`) são lógica pura sem Pygame; `app.py` só converte teclas em eventos do fluxo, mede `dt` e desenha | ✅ |
| II. Test-first para regras | Cada regra de tempo/fase (duração das partículas, pulso, tremor, contagem, entrada/saída, entradas ignoradas) entra por um teste que falha antes | ✅ |
| III. Simulação determinística | `flow.py` recebe `dt_ms` de fora (não lê relógio); efeitos usam um `random.Random` **separado** do RNG do jogo, semeado a partir da mesma seed, então a sequência de comidas da 001 não muda | ✅ |
| IV. Sem complexidade prematura | Uma enum de fases + um `update(dt)`; efeitos são funções de "progresso de 0 a 1". Sem engine de animação, sem ECS, sem scene graph. Ver Complexity Tracking | ✅ (justificado) |
| V. Jogável em todo checkpoint | Cada fase do `tasks.md` termina com `python -m snake` abrindo e `pytest` verde | ✅ |

**Re-check pós-design (Phase 1)**: os contratos em `contracts/` expõem só tipos próprios (fases,
partículas, offsets, progresso), nada do Pygame; o `Flow` encapsula `Game` e `EndMenu` sem alterar
suas regras. Gate continua aprovado. *Revisado em 2026-11-12 após a clarificação de pulso
"punchy", mini tremor e grade 30×30: tremores e partículas usam casas como unidade, e o pulso e o
tremor seguem como funções puras do tempo.*

## Project Structure

### Documentation (this feature)

```text
specs/002-game-juice/
├── plan.md              # Este arquivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── juice-api.md     # efeitos: partículas, pulso, tremor, interpolação
│   └── flow-api.md      # fases de tela e eventos de entrada
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
src/snake/
├── core.py          # inalterado (regras da 001)
├── menu.py          # inalterado (EndMenu da 001)
├── juice.py         # NOVO: ParticleBurst, ScorePulse, ScreenShake, ease/progress (sem Pygame)
├── flow.py          # NOVO: Phase, Flow (fases de tela, relógio de passos, gatilhos de efeitos)
└── app.py           # REESCRITO: teclado → Flow, dt → Flow.update, desenho a partir do Flow

tests/
├── test_juice.py        # NOVO: durações, decaimento, determinismo dos efeitos
├── test_flow.py         # NOVO: tela inicial, contagem, partida, tremor, menu, restart
└── test_core_purity.py  # estendido: juice e flow sem pygame/time/datetime
```

**Structure Decision**: mantém o layout da 001. O relógio de 8 passos/s, que hoje vive em
`app.py`, passa para `Flow.update(dt)`, para que "a cobra só anda depois do 1" e "o menu só abre
depois do tremor" sejam testáveis sem janela.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Máquina de fases (`Flow`) com 8 fases | A spec define uma sequência obrigatória de telas e tempos (inicial → contagem → partida → tremor → menu → saída) e entradas ignoradas em fases específicas | Manter flags soltas no `app.py` tornaria essas regras impossíveis de testar sem janela (fere o Princípio II) |
