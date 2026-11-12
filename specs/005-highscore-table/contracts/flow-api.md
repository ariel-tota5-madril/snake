# Contract: `snake.flow` — delta da feature 005

Tudo da 004 continua valendo, exceto as mudanças abaixo.

## Construtor

`Flow(seed=None, width=30, height=30, settings=None, settings_path=None,
highscores_path: Path | None = None)` — placar carregado de `highscores_path` (vazio se `None`);
salvo nele ao fim de cada partida.

## Fases novas

`NAME_IN`, `NAME`, `NAME_OUT` (entrada de nome, com `ui_progress` como os outros painéis).
`MENU_IN`/`MENU`/`MENU_OUT` continuam existindo, agora como a tela do placar.

## Entradas

| Método | Mudança |
|--------|---------|
| `type_text(ch: str)` | **novo**: em `NAME` (ou `NAME_IN`, concluindo a entrada) digita; `NAME_TYPE` se mudou |
| `backspace()` | **novo**: em `NAME` apaga; `NAME_TYPE` se mudou |
| `confirm()` | `TITLE`: `PLAY` → `TITLE_OUT` → `NAME_IN`; `QUIT` → `quit_requested`; `NAME`: confirma nome válido; `MENU`: pula animação ou confirma opção |
| `escape()` | `NAME`: volta para `TITLE_IN`; `MENU`: "Tela inicial" |
| `direction()` | `MENU`: ↑/↓ rolam, ←/→ trocam a opção (só com a animação terminada) |

## Consultas novas

| Atributo | Significado |
|----------|-------------|
| `accepts_text: bool` | `True` em `NAME_IN`/`NAME` (o adaptador manda letras como texto, não WASD) |
| `name_entry: NameEntry \| None` | campo de nome ativo |
| `player_name: str \| None` | último nome confirmado na sessão |
| `highscores: Highscores` | placar atual |
| `scoreboard: Scoreboard \| None` | tela do placar ativa |
| `menu: Menu \| None` | opções do placar (`END_OPTIONS`) |

## Garantias

- O placar é salvo uma vez por partida, no momento em que ela termina.
- "Jogar de novo" não passa pela entrada de nome; "Tela inicial" sim (já preenchida).
- `TITLE_IN` continua ignorando setas (002).
