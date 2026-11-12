# Research: Highscore

## 1. Regra do placar

- **Decision**: `rank_for(score) = quantidade de entradas com pontos >= score`; entra se
  `rank < 10`. Inserir nessa posição põe o novo resultado abaixo dos empatados (mais antigo acima,
  FR-006) e corta a lista em 10. Cada partida é uma entrada (mesmo nome pode repetir).
- **Rationale**: uma regra só cobre placar vazio, com espaço, cheio e empates.

## 2. Persistência

- **Decision**: JSON `[{"name": "ANA", "score": 42}, ...]` em `~/.config/snake/highscores.json`,
  gravado ao fim de cada partida (antes da animação). Leitura tolerante: arquivo ausente/JSON
  inválido → vazio; entradas com nome inválido (não-texto, vazio, > 10 caracteres) ou pontos
  inválidos (não-inteiro, bool, negativo) são descartadas; o restante é reordenado (estável) e
  cortado em 10.
- **Rationale**: FR-007, SC-005; mesmo padrão do `settings.json` da 003.

## 3. Entrada de nome

- **Decision**: `NameEntry(initial)`: `type(ch) -> bool` aceita letras e dígitos ASCII e espaço
  enquanto houver espaço (10); `backspace() -> bool`; `value` = texto sem espaços nas pontas;
  `confirmable` = `value != ""`. O `app.py` repassa `event.unicode` como texto e Backspace/Enter/
  Esc como teclas; WASD só vira direção quando `flow.accepts_text` é falso.
- **Rationale**: FR-002 e FR-011; letras acentuadas ficam de fora porque a fonte padrão e o placar
  em estilo arcade usam ASCII.

## 4. Linha do tempo do foguete

Coordenadas do placar em "linhas" (0 = 1º lugar). `N` = linhas do placar final, `V = 5` visíveis.

| Etapa | Duração | Acontece |
|-------|---------|----------|
| `IGNITION` | 700 ms | nome na linha de partida `y0 = N − 1` (chão); tremor (±0,08 linha); chama; som de ignição; se o placar estava cheio, o antigo 10º explode e cai (impacto) no início |
| `CLIMB` | depende da distância | aceleração constante até `V_MAX = 5 linhas/s` (atingida em 1,5 linha), depois velocidade constante; som de decolagem no início |
| `LANDING` | 300 ms | nome no lugar; som de pouso; chama para |
| `FIRST_PLACE` | 1 000 ms | só se `rank == 0`: "1ST PLACE!" cresce e assenta; fanfarra |
| `DONE` | — | opções ativas; rolagem manual liberada |

- Tempo de subida para `d` linhas: `d ≤ 1,5`: `√(2d/a)`, com `a = V_MAX²/3`; senão
  `(d + 1,5)/V_MAX`. Pior caso (`d = 9`): 2,1 s → animação total ≤ 0,7 + 2,1 + 0,3 + 1,0 = 4,1 s
  (SC-003).
- **Câmera** (resposta da clarificação): `view = clamp(min(view0, y − FOLLOW_AT), 0, N − V)` com
  `view0 = max(0, N − V)` (abre mostrando o fim da lista) e `FOLLOW_AT = 1,6` linhas da borda de
  cima (um pouco acima do meio de 5 linhas). Assim: o foguete sobe na tela até 1,6; depois a lista
  desce na mesma velocidade; quando `view` chega a 0 (1º lugar na tela), o foguete volta a subir
  na tela com a mesma velocidade máxima.
- **Impactos**: a entrada que estava na linha `k` (para `k = y0 − 1` até `rank`) é atingida quando
  `y ≤ k + 0,5`; ela vira um `Shatter` que espalha as letras (300 ms) e as remonta na linha
  `k + 1` (350 ms). Som de impacto em cada uma.
- **Sem subida** (`rank == y0`): ignição → pouso (sem som de decolagem).
- **Não qualificou**: sem foguete; `DONE` direto; placar aberto no fim da lista; resultado do
  jogador mostrado abaixo.
- **Pular** (Enter): todos os shatters concluídos, foguete na linha `rank`, câmera no valor final,
  "1ST PLACE!" visível se for o caso, `DONE`.

## 5. Explosão das letras (`Shatter`)

- **Decision**: cada caractere de `nome + pontos` ganha velocidade aleatória (2–6 linhas/s em
  qualquer direção); fase de espalhar 300 ms com `ease_out`; fase de remontar 350 ms com
  `ease_in_out` de volta ao deslocamento 0 enquanto a linha-base desliza de `k` para `k + 1`.
  Para o 10º expulso: sem remontar; gravidade de 12 linhas/s² e 800 ms de vida (cai pela base).
- **Rationale**: "letras e pontos espalhando e se refazendo no slot de baixo" (US3/FR-013/FR-013a).

## 6. Chama do foguete

- **Decision**: a cada 40 ms em `IGNITION`/`CLIMB`, uma `ParticleBurst` de 5 partículas com
  `angle=(π/2 − 0,5, π/2 + 0,5)` (para baixo), 2–5 linhas/s, 350 ms, `tint="flame"`, origem na
  base do nome (`x = 0`, centro do placar; `y = y + 1`).

## 7. Sons novos

| Evento | Som | Volume relativo |
|--------|-----|-----------------|
| `NAME_TYPE` | quadrada 25% 1 500 Hz, 25 ms | 0,35 |
| `ROCKET_IGNITE` | ruído com clock subindo 600 → 2 500 Hz, 700 ms | 0,6 |
| `ROCKET_LAUNCH` | ruído 3 → 9 kHz + quadrada 12,5% 300 → 1 200 Hz, 400 ms | 0,8 |
| `ROCKET_HIT` | ruído 5 kHz → 800 Hz 120 ms + quadrada 200 Hz | 0,7 |
| `ROCKET_LAND` | triangular 200 → 80 Hz, 200 ms | 0,8 |
| `FIRST_PLACE` | fanfarra (jingle): arpejo C5–E5–G5–C6 + C6 longo, baixo triangular | jingle |

## 8. Desenho

- Painel 320×540 (×S) centralizado: título "HIGHSCORES", área recortada de 5 linhas (linha de
  70×S), setas ▲/▼ quando há conteúdo fora da vista, resultado de quem não entrou abaixo, opções
  lado a lado na base (←/→).
- Cada linha: número da posição (fixo na linha), nome à esquerda e pontos à direita; desenhados
  caractere a caractere em largura fixa (estilo arcade), o que permite a explosão por letra.
- Entrada de nome: painel com "Seu nome", o campo com cursor piscando e "Enter para jogar".
