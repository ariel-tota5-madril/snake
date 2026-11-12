# Contract: `snake.flow` — delta da feature 004

Tudo da 003 continua valendo, exceto as mudanças abaixo.

## Passo

O intervalo entre passos em `PLAYING` passa a ser `frenzy.step_interval_ms(len(game.snake),
frenzy=game.in_frenzy)`, recalculado a cada passo. `STEP_MS` deixa de ser usado no passo (fica
como referência do intervalo inicial).

## Fases novas

| Fase | Duração | Entradas | Observações |
|------|---------|----------|-------------|
| `FRENZY_INTRO` | 1 900 ms | ignoradas | especiais já no tabuleiro; carimbos; termina em `PLAYING` com o cronômetro correndo |
| `SURVIVED` | 1 500 ms | ignoradas | fruta normal de volta; termina em `PLAYING` normal |
| `TIMEOUT` | 1 200 ms | ignoradas | `game.status == GAME_OVER`; termina em `MENU_IN` |

## Consultas novas

| Atributo | Significado |
|----------|-------------|
| `frenzy: Frenzy \| None` | cronômetro do modo; `None` fora do Frenzy |
| `frenzy_count: int` | Frenzies iniciados nesta partida |
| `timer_visible: bool` | `True` em `PLAYING`/pausa com Frenzy ativo e em `TIMEOUT` |
| `timer_pulse: ScorePulse` | pulso do cronômetro nos segundos de aviso |
| `stamp_scales -> tuple[float \| None, float \| None]` | escala de "FEEDING" e "FRENZY" em `FRENZY_INTRO` (`None` = ainda não entrou; 4,0 → 1,0) |
| `stamp_alpha -> float` | 1,0 até 1 600 ms; cai a 0 até 1 900 ms |
| `survived_progress -> float` | 0 → 1 (entrada), 1 (fica), 1 → 0 (saída); 0 fora de `SURVIVED` |
| `timeout_blink -> bool` | em `TIMEOUT`, alterna a cada 150 ms (vermelho aceso/apagado) |
| `stamp_origins -> tuple[Cell, Cell]` | centro (em casas) de cada palavra, para o desenho e os detritos |

## Eventos sonoros novos

`BOOM`, `TIMER_TICK`, `TIMEOUT_ALARM`, `MUSIC_FRENZY` (momentos em `data-model.md`).

## Garantias

- O Frenzy começa exatamente nos placares `threshold(0)`, `threshold(1)`, … e em nenhum outro.
- Durante o Frenzy, o placar e o comprimento da cobra não mudam; ao sair com sucesso, o
  comprimento é o mesmo da entrada.
- O cronômetro só desconta `dt` em `PLAYING`.
- No mesmo quadro, comer a última especial vence o tempo esgotado.
- Restart, "Tela inicial" e colisão descartam o Frenzy; uma nova partida começa sem Frenzy, com
  `frenzy_count = 0` e velocidade inicial.
- Mesmas entradas e `dt` → mesmas fases, mesmas especiais e mesmos eventos sonoros.
