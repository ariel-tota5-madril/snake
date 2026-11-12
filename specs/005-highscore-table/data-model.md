# Data Model: Highscore

## `highscores.py`

| Nome | Definição |
|------|-----------|
| `CAPACITY = 10`, `NAME_MAX = 10` | limites |
| `Entry(name: str, score: int)` | dataclass imutável |
| `Highscores.entries: list[Entry]` | ordem decrescente de pontos; empates por ordem de chegada |
| `rank_for(score) -> int \| None` | `#entradas com score >= score`, ou `None` se ≥ 10 |
| `insert(name, score) -> int \| None` | insere na posição, corta em 10, devolve a posição |
| `load(path)` / `save(path)` | JSON tolerante (research.md §2) |

## `menu.py` (delta)

| Nome | Definição |
|------|-----------|
| `MenuOption.QUIT` | rótulo passa a ser "Sair" |
| `MenuOption.PLAY_AGAIN` | "Jogar de novo" |
| `TITLE_OPTIONS` | `(PLAY, OPTIONS, QUIT)` |
| `END_OPTIONS` | `(PLAY_AGAIN, TITLE)` |
| `NameEntry(initial="")` | `text`, `type(ch) -> bool`, `backspace() -> bool`, `value`, `confirmable` |

## `scoreboard.py`

| Nome | Definição |
|------|-----------|
| `VISIBLE_ROWS = 5` | linhas visíveis |
| `ScorePhase` | `IGNITION`, `CLIMB`, `LANDING`, `FIRST_PLACE`, `DONE` |
| `Scoreboard(before, after, rank, player, rng)` | `before`/`after`: listas de `Entry`; `rank`: posição nova ou `None` |
| `phase`, `done` | etapa atual |
| `rocket_y: float \| None` | linha (fracionária) do nome do jogador durante a animação |
| `rocket_offset: (dx, dy)` | tremor da ignição (em linhas) |
| `view_top: float` | primeira linha visível (câmera) |
| `rows() -> list[RowView]` | linhas estáticas a desenhar: `(y, entry, is_player)` |
| `shatters: list[Shatter]` | explosões ativas |
| `bursts: list[ParticleBurst]` | chama (coordenadas em linhas; x = 0 no centro) |
| `first_place: float` | 0 → 1 (entrada do "1ST PLACE!"); 1 ao fim; 0 se não é 1º |
| `outside: Entry \| None` | resultado de quem não entrou |
| `update(dt)`, `skip()`, `scroll(direction) -> bool` | `scroll` só em `DONE` |
| `drain_events() -> list[str]` | `"ignite"`, `"launch"`, `"hit"`, `"land"`, `"first"` |

### `Shatter`

| Campo | Regra |
|-------|-------|
| `entry`, `from_y`, `to_y \| None` | `to_y = None`: expulso (cai) |
| `offsets() -> list[(dx, dy)]` | deslocamento de cada caractere de `name + str(score)` |
| `base_y` | linha-base atual (desliza de `from_y` a `to_y` na remontagem) |
| `alpha` | 1; no expulso, cai a 0 ao fim |
| `done` | após 650 ms (remonta) ou 800 ms (expulso) |

## Flow — delta

### Fases

```text
TITLE ──Jogar──▶ TITLE_OUT ──▶ NAME_IN ──▶ NAME ──Enter (nome válido)──▶ NAME_OUT ──▶ COUNTDOWN
NAME ──Esc──▶ TITLE_IN (sem trocar a música)
TITLE ──Sair──▶ quit_requested (CONFIRM)
fim da partida (SHAKING/WON/TIMEOUT) ──▶ salva placar ──▶ MENU_IN ──▶ MENU (placar animando → opções)
MENU ──Jogar de novo──▶ MENU_OUT ──▶ COUNTDOWN (restart, mesmo nome)
MENU ──Tela inicial / Esc──▶ MENU_OUT ──▶ TITLE_IN (restart, MUSIC_TITLE)
```

### Entradas em `MENU`

| Entrada | Animação rodando | Animação terminada |
|---------|------------------|--------------------|
| ↑/↓ (W/S) | ignorada | rola (NAV se mudou) |
| ←/→ (A/D) | ignorada | troca a opção (NAV se mudou) |
| Enter | pula a animação | confirma a opção (CONFIRM) |
| Esc | vai para "Tela inicial" | vai para "Tela inicial" |

### Eventos sonoros novos

`NAME_TYPE` (digitar/apagar com mudança), `ROCKET_IGNITE`, `ROCKET_LAUNCH`, `ROCKET_HIT`,
`ROCKET_LAND`, `FIRST_PLACE` — os cinco últimos vêm de `scoreboard.drain_events()`.

## Revisão pós-clarificação

| Nome | Mudança |
|------|---------|
| `MenuOption.RANKING` | "Ranking"; `TITLE_OPTIONS = (PLAY, RANKING, OPTIONS, QUIT)` |
| `Scoreboard.viewer(entries)` | consulta: `rank=None`, sem `outside`, `view_top = 0`, `done` |
| `Scoreboard.empty_slots() -> list[int]` | posições 0–9 a desenhar como "---" |
| `RowView.red: float` | 0 → 1 em 400 ms após o impacto; fica 1 |
| `Shatter.red: float` | idem, para as letras em voo |
| plataforma | `rocket_y` começa em 10.0 (fora das posições); `view_top` começa em 6 |
| Flow | fases `RANKING_IN`/`RANKING`/`RANKING_OUT`; `ranking: Scoreboard \| None` |
