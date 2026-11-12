# Research: Game juice

Não havia itens NEEDS CLARIFICATION no Technical Context. Decisões técnicas:

## 1. Onde vive o tempo das animações

- **Decision**: módulos puros recebem `dt_ms` (milissegundos desde o último quadro) por
  `update(dt_ms)`; só `app.py` lê `pygame.time.Clock`.
- **Rationale**: Princípio III — nenhum módulo de regra lê o relógio. Testes avançam o tempo
  chamando `update(100)` quantas vezes quiserem.
- **Alternatives considered**: animar direto no `app.py` com `pygame.time.get_ticks()` (sem
  testes possíveis para contagem, tremor e sequência de telas).

## 2. Aleatoriedade dos efeitos sem afetar o jogo

- **Decision**: o `Flow` cria dois RNGs a partir da seed: o do jogo (`random.Random(seed)`,
  igual à 001) e o dos efeitos (`random.Random(f"juice-{seed}")`).
- **Rationale**: partículas e tremor consomem números aleatórios; se usassem o RNG do jogo, a
  sequência de comidas mudaria (fere SC-005). Seed derivada mantém tudo reproduzível (FR-011).
- **Alternatives considered**: efeitos sem aleatoriedade (partículas em ângulos fixos — visual
  repetitivo); RNG global (não determinístico).

## 3. Detectar "comeu" e "colidiu" sem mexer no núcleo

- **Decision**: o `Flow` compara o estado antes/depois de cada `game.step()`: `score` aumentou →
  comeu (partículas na nova cabeça + pulso); `status` virou `GAME_OVER` → tremor; virou `WON` →
  menu direto, sem tremor.
- **Rationale**: `core.py` fica intocado (feature só visual); a comparação é trivial e testável.
- **Alternatives considered**: callbacks/eventos no `Game` (muda a API da 001 sem necessidade).

## 4. Partículas

- **Decision**: 16 partículas por explosão, ângulo uniforme e velocidade entre 2,5 e 7,5 casas/s
  (60–180 px/s com casas de 24 px) sorteados no RNG dos efeitos; vida de 600 ms; alfa e tamanho
  decaem linearmente; a explosão termina quando todas morrem. Posição em casas da grade (o
  `Flow` não conhece pixels); o adaptador converte. *Ajustado na implementação: antes era px.*
- **Rationale**: atende FR-001 (≤ 0,6 s) e cabe com folga em 60 fps com 3 explosões (48
  partículas).

## 5. Pulso do placar ("punchy")

- **Decision**: duração 300 ms em três trechos: 0–60 ms sobe de 1,0 a 1,8 (ease-out); 60–180 ms
  desce de 1,8 a 0,9 (ease-in-out); 180–300 ms sobe de 0,9 a 1,0 (ease-out). Cor: `warmth` vai
  de 0 (branco) a 1 (amarelo) nos primeiros 60 ms; `flash` (força do flash sobre a cor normal)
  cai de 1 a 0 ao longo dos 300 ms. Um novo pulso reinicia o tempo.
- **Rationale**: FR-002 revisado — pico em 60 ms, quique a ~0,9× e assentamento exato em 1× e na
  cor original aos 300 ms; trechos lineares por partes são fáceis de testar em pontos fixos.
- **Alternatives considered**: mola amortecida (`e^-kt·cos`): bonita, mas não termina exatamente
  em 1 aos 300 ms sem ajuste fino; o modelo por trechos atende a spec com valores exatos.

## 6. Tremores de tela (colisão e comer)

- **Decision**: um único `ScreenShake` com `trigger(amplitude, duration_ms)`, em **casas** (o
  adaptador multiplica pelo tamanho da casa). Colisão: amplitude 1/3 de casa (16 px com casas de
  48 px; os 8 px de antes com casas de 24 px), 400 ms. Comer: amplitude 1/9 de casa (≈ 5 px, um
  terço da colisão), 150 ms. Decaimento linear; ao fim, offset exatamente (0, 0). Um novo
  `trigger` substitui o tremor em andamento (colisão substitui o mini tremor).
- **Rationale**: FR-004, FR-015, SC-002; um tremor por vez basta e evita somar deslocamentos.
- **Alternatives considered**: dois objetos de tremor somados (mais estado, sem ganho visível).

## 7. Animações de UI

- **Decision**: entrada/saída de 300 ms com "ease-out cubic" (`1 − (1 − p)³`); tela inicial e
  janela de fim crescem de 0,8 para 1,0 de escala com alfa de 0 a 1 (saída: o inverso); números da
  contagem aparecem grandes e encolhem a cada segundo; o placar entra deslizando de cima.
- **Rationale**: todas ≤ 0,4 s (FR-007, FR-008); uma função de interpolação basta (Princípio IV).

## 8. Tamanho da grade e da janela

- **Decision**: o `Flow` cria o jogo com `width = height = 30`; o adaptador usa `CELL = 48`
  (janela 1440×1440) e calcula fontes e tamanhos de efeitos a partir de `CELL`
  (`UI_SCALE = CELL / 24 = 2`).
- **Rationale**: FR-014; o padrão 20×20 do `Game` continua sendo o da 001 e seus testes não
  mudam; o jogo da 002 escolhe 30×30 na camada que monta a partida.
- **Alternatives considered**: mudar o padrão de `Game` para 30×30 (quebraria a spec e os testes
  da 001 sem necessidade).

## 9. Fases de tela

- **Decision**: enum `Phase` com `TITLE_IN`, `TITLE`, `TITLE_OUT`, `COUNTDOWN`, `PLAYING`,
  `SHAKING`, `MENU_IN`, `MENU`, `MENU_OUT`. O jogo abre em `TITLE_IN`; "Restart" leva de
  `MENU_OUT` a `COUNTDOWN`. "Quit" e fechar a janela saem de qualquer fase.
- **Rationale**: cada fase tem uma regra de entrada e de tempo da spec; nomes explícitos tornam os
  testes legíveis.
