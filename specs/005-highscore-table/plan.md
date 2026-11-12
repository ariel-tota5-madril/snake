# Implementation Plan: Highscore — nome do jogador e placar animado

**Branch**: `005-highscore-table` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-highscore-table/spec.md`

## Summary

O jogador digita o nome depois de "Jogar"; ao fim de cada partida, o menu de fim dá lugar a um
placar vertical com as 10 melhores pontuações (salvas em JSON), 5 linhas visíveis e rolagem. Se a
pontuação entra, o nome vira um foguete: ignição com tremor (o antigo 10º explode e cai para fora
se o placar estava cheio), decolagem acelerando até a velocidade máxima, câmera seguindo, nomes
ultrapassados explodindo e se remontando uma linha abaixo, pouso e "1ST PLACE!" no 1º lugar.
Depois, "Jogar de novo" ou "Tela inicial". A tela inicial ganha "Sair". WASD vale como setas fora
da entrada de nome.

Abordagem técnica (mesmo padrão das features anteriores):

- **`highscores.py`** (novo, puro): entradas, regra de qualificação/inserção (top 10, empate com o
  mais antigo acima) e persistência tolerante a arquivo inválido.
- **`scoreboard.py`** (novo, puro): a tela do placar — linha do tempo do foguete, câmera, explosões
  ("shatters"), rolagem, pular animação e eventos sonoros, tudo por `update(dt)` e RNG injetado.
- **`menu.py`**: `NameEntry` (texto até 10 caracteres) e as opções novas (título com "Sair", fim
  com "Jogar de novo"/"Tela inicial").
- **`flow.py`**: fases `NAME_IN`/`NAME`/`NAME_OUT`; `MENU_*` passam a ser a tela do placar;
  entradas de texto (`type_text`, `backspace`); salvar o placar ao fim da partida.
- **`juice.py`**: `ParticleBurst` ganha `angle` (faixa de ângulo) para a chama do foguete.
- **`sounds.py`**: digitação, ignição, decolagem, impacto, pouso e fanfarra do 1º lugar.
- **`app.py`**: entrada de nome, painel do placar (recorte de 5 linhas, letras por caractere para
  as explosões), WASD, caminho do arquivo do placar.

## Technical Context

**Language/Version**: Python 3.12 (compatível com 3.12+; `.venv` local em 3.13)

**Primary Dependencies**: Pygame 2.6 (só em `app.py`/`audio.py`); biblioteca padrão nos módulos
puros — **sem dependências novas**

**Storage**: `~/.config/snake/highscores.json` — lista ordenada `[{"name": str, "score": int}]`
(caminho injetável)

**Testing**: pytest sobre `highscores`, `scoreboard`, `menu`, `juice`, `sounds` e `flow`

**Target Platform**: desktop (janela 1440×1440)

**Project Type**: desktop-app (jogo local)

**Performance Goals**: 60 fps durante a animação (SC-004); animação ≤ 5 s (SC-003)

**Constraints**: placar corrompido nunca impede o jogo de abrir (SC-005); mesma seed → mesma
animação (Princípio III)

**Scale/Scope**: 2 módulos novos; `menu.py`, `flow.py`, `juice.py`, `sounds.py` e `app.py`
alterados; 6 eventos sonoros novos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | Placar, animação, entrada de nome e fluxo são puros; `app.py` só traduz teclas/texto e desenha; persistência em `highscores.py` sem Pygame | ✅ |
| II. Test-first para regras | Qualificação, ordenação, empate, persistência tolerante, linha do tempo do foguete, câmera, impactos, pular, rolagem, entrada de nome e transições entram por testes que falham antes | ✅ |
| III. Simulação determinística | Animação por `dt` injetado; partículas e explosões usam o RNG de efeitos do `Flow` | ✅ |
| IV. Sem complexidade prematura | Uma tela de placar como objeto puro com fases internas simples; sem engine de animação. Ver Complexity Tracking | ✅ (justificado) |
| V. Jogável em todo checkpoint | US1 (nome) e US2 (placar sem animação) são jogáveis antes da US3 (foguete) e da US4 (sons) | ✅ |

**Re-check pós-design (Phase 1)**: contratos expõem só tipos próprios (`Entry`, `Highscores`,
`Scoreboard`, `Shatter`, `NameEntry`); Pygame continua restrito a `app.py`/`audio.py`. Aprovado.

## Project Structure

### Documentation (this feature)

```text
specs/005-highscore-table/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── highscores-api.md    # highscores + scoreboard + NameEntry
│   └── flow-api.md          # delta sobre a 004
└── tasks.md
```

### Source Code (repository root)

```text
src/snake/
├── highscores.py   # NOVO: Entry, Highscores (rank_for, insert, load, save)
├── scoreboard.py   # NOVO: Scoreboard (foguete, câmera, shatters, rolagem, eventos), Shatter
├── menu.py         # ALTERADO: NameEntry; TITLE_OPTIONS com QUIT ("Sair"); END_OPTIONS novos
├── juice.py        # ALTERADO: ParticleBurst(angle=...)
├── flow.py         # ALTERADO: NAME_*; placar no fim; type_text/backspace; highscores_path
├── sounds.py       # ALTERADO: NAME_TYPE, ROCKET_*, FIRST_PLACE
└── app.py          # ALTERADO: entrada de nome, painel do placar, WASD

tests/
├── test_highscores.py   # NOVO
├── test_scoreboard.py   # NOVO
├── test_menu.py         # ajustado (opções novas, NameEntry)
├── test_juice.py        # ampliado (angle)
├── test_sounds.py       # ampliado
├── test_flow.py         # ajustado (nome antes da contagem; placar no lugar do menu de fim)
└── test_core_purity.py  # ampliado (highscores, scoreboard)
```

**Structure Decision**: o placar é uma tela com muita lógica própria (tempo, câmera, explosões),
então vive em `scoreboard.py` e o `Flow` só o cria, repassa `dt`/teclas e drena seus eventos —
o `flow.py` (já grande) não absorve a animação.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 3 fases novas no `Flow` (`NAME_IN`, `NAME`, `NAME_OUT`) | A entrada de nome é uma tela com entrada/saída animada como as demais | Um campo dentro de `TITLE` misturaria o menu da tela inicial com digitação (WASD/letras) |
| Módulo `scoreboard.py` com fases internas | A animação tem 5 etapas, câmera, explosões e eventos sincronizados | Colocar no `Flow` dobraria seu tamanho e misturaria telas com animação |
