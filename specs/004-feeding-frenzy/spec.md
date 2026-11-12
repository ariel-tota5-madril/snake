# Feature Specification: Feeding Frenzy — velocidade progressiva e modo de sobrevivência

**Feature Branch**: `004-feeding-frenzy`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "feeding-frenezy vamos fazer um modo de jogo que acontece durante a gameplay normal, chamada feeding frenezy. Primeiro, uma regra geral do jogo deve ser criada (ou garantida se existe), a cobra fica cada vez mais rapida conforme ela fica maior. Fora isso, começando em 10 pontos, e aumentando logaritmicamente, ele entra no modo feeding frenezy. Especificação do modo FF: Nesse momento, a cobra vai aumentar consideravelmente de tamanho, e 10 frutas de outra cor vão aparecer na tela junto com um timer relativamente grande no centro da tela na parte superior, com 20s. O objetivo eh comer todas as frutas especiais antes do tempo acabar. Se acabar antes de comer todas, game over. Senão, volta ao jogo normal. Durante o FF, a cobra não cresce, e os pontos não sobem. Eh um survivability test. VFX e SFX do FF: O inicio do FF deve pausar o jogo e música, e a palavra FEEDING e a palavra FRENEZY devem aparecer na diagonal, centralizada na tela, com FEEDING roxo e FRENEZY amarelo, entrando em uma animação de stamp, comecando com escala grande e descendo até a original, como se fosse uma porrada na tela estampando cada uma das 2 palavras. Um SFX de boom pra cada uma, e particulas em volta na hora do impacto, como se tivesse danificado a area que ela chegou, dado o tamanho da força. A música deve mudar pra algo tenso e rápido durante o FF, que começa a tocar depois da animação das palavras. Ao terminar, deve aparecer a palavra SURVIVED! em azul, com um efeito suave de entrada, pausando o jogo para a animação da palavra, e resumindo o jogo ao sair a palavra"

## Clarifications

### Session 2026-11-12

- Q: Quanto a cobra cresce no início do Feeding Frenzy? → A: Ela não cresce: o modo aumenta a
  velocidade (1,5× a normal, mínimo de 50 ms por passo); a cobra entra e sai com o mesmo tamanho.
- Q: Qual a curva de velocidade normal? → A: 125 ms por passo com 3 segmentos, −1 ms por segmento
  a mais, até o mínimo de 70 ms.
- Q: Em quais pontuações o Feeding Frenzy começa? → A: 10, 20, 40, 80… (dobra a cada vez).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cobra mais rápida conforme cresce (Priority: P1)

Hoje a cobra anda sempre na mesma velocidade. Passa a valer uma regra geral: quanto maior a cobra,
mais rápido ela anda, até um limite que ainda seja jogável.

**Why this priority**: é a regra base que dá progressão de dificuldade à partida inteira. Funciona
sozinha, mesmo sem o modo especial.

**Independent Test**: jogar uma partida comendo várias frutas e perceber a cobra acelerar a cada
fruta, sem nunca passar do limite de velocidade.

**Acceptance Scenarios**:

1. **Given** uma partida que acabou de começar (cobra com 3 segmentos), **When** a cobra anda,
   **Then** ela anda na velocidade atual do jogo (um passo a cada 125 ms).
2. **Given** uma partida em andamento, **When** a cobra come uma fruta e cresce, **Then** o
   intervalo entre passos diminui 1 ms (FR-002).
3. **Given** uma cobra já no tamanho em que atinge a velocidade máxima, **When** ela cresce mais,
   **Then** a velocidade não aumenta além do limite.
4. **Given** o jogador reinicia a partida, **When** a nova partida começa, **Then** a velocidade
   volta à inicial.

---

### User Story 2 - Modo Feeding Frenzy (Priority: P1)

Ao atingir certas pontuações (a primeira é 10, e as seguintes cada vez mais espaçadas), a partida
entra em Feeding Frenzy: a cobra fica bem mais rápida, a fruta normal some, 10 frutas
especiais de outra cor aparecem e um cronômetro de 20 s surge no topo da tela. O jogador precisa
comer todas as frutas especiais antes do tempo acabar. Se conseguir, a partida volta ao normal; se
o tempo acabar, é fim de jogo. Durante o modo, a cobra não cresce ao comer e o placar não sobe:
ela entra e sai do modo com o mesmo tamanho.

**Why this priority**: é o coração da feature: um teste de sobrevivência que interrompe a partida
normal e cria picos de tensão.

**Independent Test**: começar uma partida, chegar a 10 pontos e verificar que o modo começa;
comer as 10 frutas especiais em menos de 20 s e ver a partida voltar ao normal; repetir deixando o
tempo acabar e ver o fim de jogo.

**Acceptance Scenarios**:

1. **Given** uma partida normal com 9 pontos, **When** a cobra come uma fruta e chega a 10 pontos,
   **Then** começa o Feeding Frenzy.
2. **Given** o Feeding Frenzy começou, **When** a partida volta a andar após a abertura, **Then** a
   cobra está consideravelmente mais rápida (FR-006) e com o mesmo tamanho de antes, a fruta
   normal não está no tabuleiro, há 10 frutas especiais de cor diferente em casas livres e o cronômetro mostra 20 s no centro do topo da tela.
3. **Given** o Feeding Frenzy em andamento, **When** a cobra come uma fruta especial, **Then** a
   fruta some, a cobra não cresce, o placar não muda e o contador de frutas restantes diminui.
4. **Given** o Feeding Frenzy em andamento, **When** a cobra come a última fruta especial antes do
   cronômetro chegar a 0, **Then** o modo termina com sucesso e a partida volta ao normal, com uma
   fruta normal no tabuleiro, a cobra com o mesmo tamanho com que entrou no modo e a velocidade de
   volta à normal para esse tamanho.
5. **Given** o Feeding Frenzy em andamento com frutas especiais restantes, **When** o cronômetro
   chega a 0, **Then** a partida termina em fim de jogo (mesmo menu de fim de partida da derrota
   normal).
6. **Given** o Feeding Frenzy em andamento, **When** a cobra bate na parede ou em si mesma,
   **Then** a partida termina em fim de jogo, como numa colisão normal.
7. **Given** o primeiro Feeding Frenzy foi superado com 10 pontos, **When** o jogador continua
   comendo frutas normais, **Then** o próximo Feeding Frenzy só começa no próximo limiar da
   sequência (FR-004): aos 20 pontos, depois aos 40, aos 80, e assim por diante.
8. **Given** o Feeding Frenzy em andamento, **When** o jogador aperta Esc, **Then** a partida pausa
   como sempre e o cronômetro também para; ao continuar, o cronômetro segue de onde parou.

---

### User Story 3 - Abertura "FEEDING FRENZY" com impacto (Priority: P2)

Quando o modo começa, o jogo e a música param e as palavras "FEEDING" (roxo) e "FRENZY" (amarelo)
entram uma de cada vez, na diagonal e centralizadas, numa animação de carimbo: começam enormes e
caem até o tamanho final como uma pancada na tela. Cada impacto tem um som de explosão ("boom") e
partículas espirrando em volta da palavra, como se a área tivesse sido danificada pela força.
Depois da segunda palavra, começa uma música tensa e rápida e a partida retoma em modo Frenzy.

**Why this priority**: é o que comunica claramente "algo grande aconteceu" e dá o clima do modo;
o modo funciona sem ela, mas perde o impacto.

**Independent Test**: chegar a 10 pontos e observar a sequência: silêncio, "FEEDING" carimbado com
boom e partículas, "FRENZY" carimbado com boom e partículas, música tensa, retomada.

**Acceptance Scenarios**:

1. **Given** a partida chegou ao limiar do Feeding Frenzy, **When** a abertura começa, **Then** a
   cobra para, a música da partida para e o cronômetro do modo ainda não corre.
2. **Given** a abertura começou, **When** a palavra "FEEDING" entra, **Then** ela aparece roxa,
   inclinada na diagonal, centralizada, começando muito maior que o tamanho final e encolhendo
   rapidamente até ele, com uma desaceleração seca no impacto.
3. **Given** "FEEDING" chegou ao tamanho final, **When** acontece o impacto, **Then** toca um boom
   e partículas espirram ao redor da palavra, com tremor de tela.
4. **Given** "FEEDING" já está estampada, **When** "FRENZY" entra, **Then** ela aparece amarela,
   na mesma diagonal, logo abaixo/ao lado de "FEEDING", com a mesma animação, boom, partículas e
   tremor.
5. **Given** as duas palavras estamparam, **When** a abertura termina, **Then** as palavras saem
   da tela, a música do Frenzy (tensa e rápida, 8-bit) começa e a partida retoma com o cronômetro
   correndo.

---

### User Story 4 - "SURVIVED!" ao superar o modo (Priority: P3)

Ao comer a última fruta especial a tempo, a partida pausa e a palavra "SURVIVED!" em azul entra
com uma animação suave; quando a palavra sai, a partida volta ao normal com a música normal.

**Why this priority**: recompensa o jogador e marca a volta ao jogo normal; é o acabamento final.

**Independent Test**: superar um Feeding Frenzy e observar a pausa, a entrada suave de
"SURVIVED!", a saída e a retomada com a música da partida.

**Acceptance Scenarios**:

1. **Given** o Feeding Frenzy em andamento, **When** a cobra come a última fruta especial,
   **Then** a cobra para, o cronômetro some, a música do Frenzy para e "SURVIVED!" aparece em
   azul, centralizada, entrando suavemente (sem o impacto do carimbo).
2. **Given** "SURVIVED!" está na tela, **When** a animação termina e a palavra sai, **Then** a
   partida retoma em modo normal, com a música da partida voltando a tocar.

---

### Edge Cases

- Uma fruta normal levaria o placar além do limiar? Não é possível: cada fruta normal vale 1 ponto,
  então o placar passa exatamente por cada limiar.
- Não há 10 casas livres para as frutas especiais (cobra muito grande): aparecem tantas quantas couberem;
  o modo termina com sucesso quando todas as que apareceram forem comidas. Se não houver nenhuma
  casa livre, o modo não começa.
- A fruta normal que leva o placar ao limiar faz a cobra crescer normalmente (ela é do jogo
  normal); a partir daí, o tamanho fica fixo até o fim do modo.
- O cronômetro chega a 0 no mesmo passo em que a cobra come a última fruta especial: comer vence
  (o jogador é favorecido).
- O cronômetro chega a 0 no mesmo passo em que a cobra colide: é fim de jogo de qualquer forma.
- Pausa (Esc) durante a abertura "FEEDING FRENZY" ou durante "SURVIVED!": as animações não são
  interrompidas por pausa; Esc só pausa enquanto a cobra está andando.
- Fim de jogo durante o Feeding Frenzy, depois Restart: a nova partida começa no modo normal, com
  velocidade inicial, sequência de limiares do início e a música normal.
- "Tela inicial" no menu de pausa durante o Frenzy: abandona a partida, como sempre; a música do
  Frenzy para e a da tela inicial toca.
- Teclas de direção durante a abertura ou "SURVIVED!": são ignoradas (a cobra está parada).

## Requirements *(mandatory)*

### Functional Requirements

**Velocidade progressiva**

- **FR-001**: A velocidade da cobra DEVE depender do seu tamanho: quanto mais segmentos, menor o
  intervalo entre passos.
- **FR-002**: A curva de velocidade DEVE partir de um passo a cada 125 ms com 3 segmentos e
  diminuir 1 ms por segmento a mais, até o mínimo de 70 ms (atingido com 58 segmentos); a
  velocidade normal nunca ultrapassa esse limite.
- **FR-003**: A velocidade DEVE ser recalculada sempre que o tamanho da cobra muda e voltar à
  inicial ao reiniciar a partida.

**Feeding Frenzy — regras**

- **FR-004**: O Feeding Frenzy DEVE começar quando o placar atinge um limiar da sequência
  10, 20, 40, 80, 160… (cada limiar é o dobro do anterior).
- **FR-005**: Ao começar o modo, a fruta normal DEVE sair do tabuleiro e 10 frutas especiais, de
  cor claramente diferente da fruta normal, DEVEM aparecer em casas livres escolhidas
  aleatoriamente (reprodutíveis com a mesma semente).
- **FR-006**: Durante o modo, a cobra DEVE andar consideravelmente mais rápido: 1,5× a
  velocidade normal para o seu tamanho, com intervalo mínimo de 50 ms entre passos. O tamanho da
  cobra NÃO muda: ela entra e sai do modo com o mesmo número de segmentos. Ao sair do modo com
  sucesso, a velocidade volta à da curva normal (FR-002).
- **FR-007**: Durante o modo, comer uma fruta especial NÃO DEVE fazer a cobra crescer nem aumentar
  o placar.
- **FR-008**: O modo DEVE ter um cronômetro de 20 s que só corre enquanto a cobra está andando (não
  corre durante a abertura, a pausa ou "SURVIVED!").
- **FR-009**: Comer todas as frutas especiais antes do cronômetro chegar a 0 DEVE encerrar o modo
  com sucesso; uma fruta normal DEVE reaparecer numa casa livre e a partida segue normal.
- **FR-010**: Se o cronômetro chegar a 0 com frutas especiais restantes, a partida DEVE terminar
  em fim de jogo, com o mesmo fluxo, sons e menu da derrota por colisão.
- **FR-011**: Colisões durante o modo DEVEM terminar a partida como no jogo normal.

**Feeding Frenzy — visual e som**

- **FR-012**: O cronômetro DEVE aparecer grande, centralizado no topo da tela, mostrando os
  segundos restantes, durante todo o tempo em que o modo está ativo e a cobra anda.
- **FR-013**: A abertura DEVE parar a cobra e a música e mostrar "FEEDING" (roxo) e depois
  "FRENZY" (amarelo), na diagonal e centralizadas, cada uma com animação de carimbo (começa
  bem maior que o tamanho final e cai rápido até ele).
- **FR-014**: Cada impacto de palavra DEVE tocar um som de explosão 8-bit ("boom") e gerar
  partículas ao redor da palavra, acompanhado de tremor de tela.
- **FR-015**: Ao fim da abertura, DEVE começar uma música 8-bit tensa e rápida, exclusiva do
  modo, em loop, que substitui a música da partida enquanto o modo durar.
- **FR-016**: Ao comer uma fruta especial, DEVEM aparecer partículas da cor da fruta especial e
  tocar o som de coleta, sem o pulso do placar (o placar não muda).
- **FR-017**: Ao superar o modo, a partida DEVE parar, a música do modo parar e "SURVIVED!" em
  azul DEVE entrar com animação suave e depois sair; ao sair, a partida retoma com a música da
  partida.
- **FR-018**: Os sons e a música do modo DEVEM respeitar os volumes de Música e Efeitos da tela de
  Opções.

### Key Entities

- **Curva de velocidade**: relação entre o tamanho da cobra e o intervalo entre passos, com valor
  inicial e limite; durante o modo, acelerada pelo bônus de velocidade.
- **Sequência de limiares**: as pontuações em que o Feeding Frenzy começa (10, 20, 40, 80…,
  dobrando a cada vez).
- **Feeding Frenzy (sessão)**: estado ativo do modo — frutas especiais restantes, tempo restante
  e fase (abertura, ativo, sobreviveu).
- **Fruta especial**: fruta de cor distinta que só existe durante o modo; não dá ponto nem
  crescimento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em toda partida, a velocidade da cobra aumenta a cada fruta normal comida até o
  limite, e nunca o ultrapassa.
- **SC-002**: 100% das vezes que o placar atinge um limiar da sequência, o Feeding Frenzy começa;
  em nenhuma outra pontuação ele começa.
- **SC-003**: Durante o modo, o placar e o tamanho da cobra permanecem constantes em 100% das
  frutas especiais comidas; a cobra sai do modo com exatamente o tamanho com que entrou.
- **SC-004**: O cronômetro do modo fica a no máximo 0,1 s do tempo real de jogo corrido (sem
  contar pausa, abertura e "SURVIVED!").
- **SC-005**: A abertura completa (duas palavras + impactos) dura no máximo 2,5 s e "SURVIVED!"
  no máximo 2 s, para não quebrar o ritmo.
- **SC-006**: Com o modo ativo (10 frutas especiais, partículas e cronômetro), o jogo mantém 60
  quadros por segundo.
- **SC-007**: A mesma semente e as mesmas entradas reproduzem exatamente as mesmas posições das
  frutas especiais e o mesmo desfecho.
- **SC-008**: Durante o modo, a cobra anda 1,5× mais rápido que fora dele com o mesmo tamanho
  (respeitando o mínimo de 50 ms por passo).

## Assumptions

- O texto exibido é "FEEDING" e "FRENZY" (grafia em inglês de *frenzy*); a descrição escreve
  "FRENEZY", tratado como erro de digitação.
- Cores: fruta especial em roxo ou dourado, distinta da fruta normal; "SURVIVED!" em azul claro.
- "Aumentar consideravelmente" no início do modo refere-se à velocidade, não ao tamanho: bônus de
  1,5× só durante o modo, podendo passar do limite normal da curva, mas nunca abaixo de 50 ms por
  passo (para continuar jogável).
- Durante a abertura, a cobra continua visível parada no tabuleiro; as palavras ficam por cima.
- A música do modo é composta pelo projeto, no mesmo estilo 8-bit da feature 003, mais rápida
  (por volta de 180 BPM) e em tom menor.
- Os limiares contam o placar total da partida; como o placar não sobe durante o modo, o próximo
  limiar sempre é alcançado depois, já no jogo normal.
- A vitória por tabuleiro cheio continua existindo; ela só pode acontecer no jogo normal, já que
  no modo a cobra não come para crescer.
- Não há indicação prévia de que o modo vai começar; a surpresa faz parte da proposta.
