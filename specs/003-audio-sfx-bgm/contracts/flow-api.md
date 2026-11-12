# Contract: `snake.flow` — delta da feature 003

Tudo da 002 continua valendo, exceto as mudanças abaixo.

## Construtor

`Flow(seed=None, width=30, height=30, settings: AudioSettings | None = None,
settings_path: Path | None = None)` — `settings` padrão carregado de `settings_path` (ou padrão
60/80 se `None`).

## Entradas

| Método | Mudança |
|--------|---------|
| `escape()` | **novo**: `PLAYING` → pausa; `PAUSE` → continuar; `OPTIONS` → voltar; demais fases: ignorado |
| `direction(LEFT/RIGHT)` | em `OPTIONS` com `MUSIC` ou `SFX` selecionado: ajusta o volume |
| `direction(UP/DOWN)` | também em `TITLE`, `PAUSE` e `OPTIONS` (e nas fases `_IN` correspondentes, concluindo a entrada) |
| `confirm()` | `TITLE`: confirma `PLAY` ou `OPTIONS`; `PAUSE`: `CONTINUE`, `OPTIONS` ou `TITLE`; `MENU`: `RESTART`, `OPTIONS` ou `QUIT`; `OPTIONS`: `BACK` |

## Consultas novas

| Atributo | Significado |
|----------|-------------|
| `title_menu`, `pause_menu`, `options_menu` | menus ativos (ou `None`) |
| `settings` | `AudioSettings` atual |
| `resume_number` | 3, 2, 1 em `RESUME`; `None` fora dela |
| `drain_sounds() -> list[SoundEvent]` | devolve e limpa os eventos sonoros acumulados |

## Garantias

- Os eventos sonoros seguem a tabela de `data-model.md`; teclas ignoradas não emitem eventos.
- Na pausa (`PAUSE_*`, `RESUME`, Opções vindas da pausa), o estado do jogo e dos efeitos não muda.
- Sair de Opções grava os volumes em `settings_path` (se definido).
- Mesmas entradas e `dt` → mesmos eventos sonoros, na mesma ordem.
