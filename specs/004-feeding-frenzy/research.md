# Research: Feeding Frenzy

## 1. Curva de velocidade

- **Decision**: `step_interval_ms(length, frenzy=False)`:
  - normal: `max(70, 125 − (length − 3))` → 125 ms com 3 segmentos, 70 ms com 58 ou mais;
  - Frenzy: `max(50, normal / 1,5)` (valor em ms, float).
- **Rationale**: FR-002 e FR-006 com os valores das clarificações. Função pura e sem estado: o
  `Flow` consulta a cada passo, então a velocidade acompanha o tamanho sem precisar de evento.
- **Alternatives considered**: guardar a velocidade como estado e alterá-la ao comer (duplica a
  fonte da verdade, que é o tamanho).

## 2. Passo com intervalo variável no `Flow`

- **Decision**: em `_update_playing`, o acumulador compara com o intervalo atual, recalculado a
  cada passo dado (`while elapsed >= interval: elapsed -= interval; step(); interval = ...`).
- **Rationale**: se a cobra cresce no meio de um quadro com dois passos, o segundo já usa o
  intervalo novo. Ao entrar ou sair de uma fase (`_go`), o acumulador zera, como hoje.

## 3. Sequência de limiares

- **Decision**: `threshold(n) = 10 × 2ⁿ` (n = 0, 1, 2…). O `Flow` guarda quantos Frenzies já
  aconteceram na partida (`frenzy_count`); o Frenzy começa quando, após um passo em que a cobra
  comeu fruta normal, `score == threshold(frenzy_count)`. Restart e "Tela inicial" zeram o
  contador.
- **Rationale**: cada fruta normal vale exatamente 1 ponto, então o placar passa por todos os
  limiares; como o placar não sobe no Frenzy, o próximo limiar sempre está à frente.

## 4. Frutas especiais no núcleo

- **Decision**: `Game.specials: dict[Cell, int]` (célula → variante 0 = roxa, 1 = dourada).
  `start_frenzy(count=10)` remove a fruta normal e sorteia `min(count, livres)` casas com
  `rng.sample` sobre a lista ordenada de casas livres; variantes alternadas pela ordem do sorteio.
  No `step`, entrar numa casa especial remove a fruta e não cresce nem pontua (a cauda anda
  normalmente). `end_frenzy()` limpa as especiais e sorteia nova fruta normal. `fail()` muda o
  status para `GAME_OVER` (tempo esgotado). `restart()` limpa as especiais.
- **Rationale**: SC-007 (mesma seed → mesmas casas) e Princípio I (o que acontece ao comer é
  regra de jogo). O RNG do jogo já é o usado para a fruta normal.
- **Alternatives considered**: frutas especiais no `Flow` (a colisão e o "comer" ficariam
  divididos entre dois módulos).

## 5. Cronômetro

- **Decision**: `Frenzy(duration_ms=20000)` em `frenzy.py`, com `remaining_ms`, `update(dt)`,
  `expired`, `seconds_left` (= teto de `remaining_ms / 1000`, mostrado em segundos inteiros) e
  `warning` (`seconds_left <= 5`). `update` devolve os segundos de aviso que acabaram de começar
  (5, 4, 3, 2, 1) para o `Flow` emitir `TIMER_TICK` e pulsar o cronômetro.
- **Rationale**: o cronômetro só anda quando o `Flow` chama `update` em `PLAYING` (FR-008); pausa,
  abertura e "SURVIVED!" não chamam. Mostrar segundos inteiros (teto) faz o "20" aparecer cheio e
  o "0" só quando acabou de fato (SC-004 se mede sobre `remaining_ms`).
- **Empate** (spec): no quadro, os passos acontecem primeiro; se a última especial foi comida,
  é sucesso, mesmo que o tempo tenha zerado no mesmo quadro.

## 6. Linha do tempo da abertura (`FRENZY_INTRO`, 1 900 ms)

| ms | Acontece |
|----|----------|
| 0 | cobra para; `MUSIC_STOP`; frutas especiais e cronômetro ainda não aparecem |
| 200–500 | "FEEDING" cai de 4× para 1× com `ease_in` (acelera até bater) |
| 500 | impacto: `BOOM`, detritos roxos ao longo da palavra, tremor (½ casa, 300 ms) |
| 800–1100 | "FRENZY" cai do mesmo jeito |
| 1100 | impacto: `BOOM`, detritos dourados, tremor |
| 1600–1900 | as duas palavras somem (alfa 1 → 0) |
| 1900 | `start_frenzy()` já feito na entrada; vira `PLAYING`; `MUSIC_FRENZY`; cronômetro corre |

- **Decision**: `start_frenzy()` acontece na entrada da fase (as frutas ficam visíveis sob as
  palavras, dando tempo de o jogador planejar), mas o cronômetro só aparece ao fim.
- **Rationale**: 1,9 s ≤ 2,5 s (SC-005). O `ease_in` dá a sensação de pancada (velocidade máxima
  no impacto); o tremor e o boom no mesmo quadro vendem a força.
- **Palavras**: "FEEDING" acima/à esquerda e "FRENZY" abaixo/à direita do centro, as duas
  giradas ~15° (subindo para a direita), formando a diagonal.

## 7. Detritos do impacto

- **Decision**: `ParticleBurst` ganha parâmetros `count`, `speed` (faixa em casas/s), `life_ms` e
  `tint` (rótulo: `"fruit"`, `"purple"`, `"gold"`). No impacto, o `Flow` cria 5 explosões ao longo
  da palavra, cada uma com 12 partículas mais rápidas (6–14 casas/s) e mais longas (900 ms) →
  60 partículas por palavra.
- **Rationale**: "como se tivesse danificado a área": pedaços espalhados ao longo de toda a
  palavra, não só no centro. Reaproveita a física e o RNG de efeitos da 002. O `Flow` não sabe
  cores: o `tint` é traduzido em RGB no `app.py`.

## 8. "SURVIVED!" (`SURVIVED`, 1 500 ms) e tempo esgotado (`TIMEOUT`, 1 200 ms)

- **SURVIVED**: na entrada, `end_frenzy()` (fruta normal volta), `MUSIC_STOP`; 0–500 ms entra
  com `ease_in_out` (alfa 0 → 1, escala 0,85 → 1, sobe ½ casa); fica até 1 000 ms; 1 000–1 500
  sai (alfa 1 → 0); ao fim, `PLAYING` e `MUSIC_GAME`. 1,5 s ≤ 2 s (SC-005).
- **TIMEOUT**: na entrada, `game.fail()`, `MUSIC_STOP`, `TIMEOUT_ALARM`; o cronômetro mostra "0"
  piscando em vermelho (4 piscadas de 300 ms); ao fim, menu de fim de partida com `LOSE`, como na
  colisão. Sem `CRASH` e sem tremor (clarificação 2).

## 9. Sons novos

| Evento | Som | Volume relativo |
|--------|-----|-----------------|
| `BOOM` | ruído com clock caindo de 4 kHz a 200 Hz + triangular de 110 → 40 Hz, 600 ms, decaimento total | 1,0 |
| `TIMER_TICK` | quadrada 12,5% a 1 760 Hz, 35 ms | 0,5 |
| `TIMEOUT_ALARM` | quadrada 50% alternando 880/660 Hz, 3 × 2 notas de 100 ms | 0,8 |
| `MUSIC_FRENZY` | 180 BPM, lá menor, 8 compassos (~10,7 s), melodia quadrada 50% em semicolcheias, baixo triangular em colcheias, chimbal de ruído a cada colcheia e bumbo nos tempos | (música) |

- **Rationale**: mesma síntese da 003 (FR-018: volumes de Música e Efeitos se aplicam porque o
  `audio.py` já multiplica por eles). A música em tom menor, mais rápida e com semicolcheias dá a
  tensão pedida; 8 compassos inteiros para loop sem estalo.
- Comer fruta especial reaproveita `EAT` e o tremor de coleta (FR-016), sem pulso nem `PULSE_POP`.

## 10. Desenho (`app.py`)

- **Carimbos**: texto renderizado uma vez em fonte grande (com contorno escuro para ler sobre o
  tabuleiro), girado uma vez e escalado por quadro com `pygame.transform.smoothscale` (2 palavras,
  custo baixo). Escala e alfa vêm do `Flow`.
- **Frutas especiais**: quadrado da cor da variante com halo que pulsa (senóide de ~1,2 s sobre o
  tempo acumulado do `app`, só visual).
- **Cronômetro**: número grande no centro do topo (onde fica o placar, que some no Frenzy) e
  "N restantes" abaixo em fonte menor; vermelho e com pulso (`ScorePulse` próprio) nos últimos
  5 s; piscando no `TIMEOUT`.
- **SURVIVED!**: azul claro, centralizado, alfa/escala/deslocamento do `Flow`.
