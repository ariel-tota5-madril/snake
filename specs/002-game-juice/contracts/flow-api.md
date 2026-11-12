# Contract: `snake.flow` (fases de tela, lógica pura)

O adaptador (`app.py`) é o único consumidor. Ele converte o teclado em chamadas abaixo, passa o
`dt_ms` de cada quadro e desenha a partir das consultas.

## `Phase`

`TITLE_IN`, `TITLE`, `TITLE_OUT`, `COUNTDOWN`, `PLAYING`, `SHAKING`, `MENU_IN`, `MENU`,
`MENU_OUT`.

## `Flow(seed: int | None = None, width: int = 30, height: int = 30)`

Cria o jogo da 001 com `random.Random(seed)` e os efeitos com um RNG separado derivado da seed.
Começa em `Phase.TITLE_IN`.

### Entradas

| Método | Efeito por fase |
|--------|-----------------|
| `direction(d: Direction)` | `PLAYING`: `game.turn(d)`. `MENU_IN`/`MENU` com ↑/↓: move a seleção (em `MENU_IN`, conclui a entrada antes). Demais fases: ignorado |
| `confirm()` | `TITLE`: vai para `TITLE_OUT`. `MENU_IN`/`MENU`: confirma a opção (em `MENU_IN`, conclui a entrada antes). Demais fases: ignorado |
| `quit()` | qualquer fase: `quit_requested = True` |
| `update(dt_ms: float)` | avança animações, efeitos, contagem e o relógio de passos (só em `PLAYING`), aplicando as transições de `data-model.md` |

`direction(UP/DOWN)` no menu usa a mesma tecla das setas; o adaptador não precisa saber a fase.

### Consultas

| Atributo | Significado |
|----------|-------------|
| `phase` | fase atual |
| `game` | o `Game` (somente leitura para desenho) |
| `menu` | `EndMenu` ou `None` |
| `countdown_number` | 3, 2, 1 em `COUNTDOWN`; `None` fora dela |
| `ui_progress` | 0→1 com easing em fases `_IN`; 1→0 em fases `_OUT`; 1 em `TITLE` e `MENU` |
| `bursts`, `pulse`, `shake` | efeitos ativos para desenho |
| `quit_requested` | o adaptador deve fechar a janela |

## Garantias

- `Flow` nunca altera as regras do `Game`: só chama `turn`, `step` e `restart` (FR-010).
- Mesma seed + mesmas entradas e `dt` → mesma sequência de estados do jogo **e** dos efeitos
  (FR-011), e a mesma sequência de comidas que a 001 produziria (SC-005).
