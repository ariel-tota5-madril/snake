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

## 5. Pulso do placar

- **Decision**: duração 300 ms; escala = 1 + 0,5·sen(π·p) (cresce e volta); cor interpolada do
  amarelo (flash) para a cor normal conforme p; um novo pulso reinicia p = 0.
- **Rationale**: FR-002 e FR-003; termina exatamente na escala 1 e na cor original.

## 6. Tremor de tela

- **Decision**: duração 400 ms, amplitude inicial 8 px, decaimento linear até 0; a cada quadro um
  deslocamento (dx, dy) sorteado em [−a, a] no RNG dos efeitos; ao fim, offset exatamente (0, 0).
- **Rationale**: FR-004 e SC-002 (volta à posição original).

## 7. Animações de UI

- **Decision**: entrada/saída de 300 ms com "ease-out cubic" (`1 − (1 − p)³`); tela inicial e
  janela de fim crescem de 0,8 para 1,0 de escala com alfa de 0 a 1 (saída: o inverso); números da
  contagem aparecem grandes e encolhem a cada segundo; o placar entra deslizando de cima.
- **Rationale**: todas ≤ 0,4 s (FR-007, FR-008); uma função de interpolação basta (Princípio IV).

## 8. Fases de tela

- **Decision**: enum `Phase` com `TITLE_IN`, `TITLE`, `TITLE_OUT`, `COUNTDOWN`, `PLAYING`,
  `SHAKING`, `MENU_IN`, `MENU`, `MENU_OUT`. O jogo abre em `TITLE_IN`; "Restart" leva de
  `MENU_OUT` a `COUNTDOWN`. "Quit" e fechar a janela saem de qualquer fase.
- **Rationale**: cada fase tem uma regra de entrada e de tempo da spec; nomes explícitos tornam os
  testes legíveis.
