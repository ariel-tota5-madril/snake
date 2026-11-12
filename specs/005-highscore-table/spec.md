# Feature Specification: Highscore — nome do jogador e placar animado

**Feature Branch**: `005-highscore-table`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "highscore - no start de cada title screen, a pessoa vai colocar seu nome, e o jogo vai começar. Vamos fazer um placar de highscore ao final, com formato vertical (maior de altura do que largura) onde vai ficar o nome e ponto da pessoa. A animação do highscore vai ser o nome com particulas simulando foguete, o nome vai tremer um pouco no lugar antes de começar um lift off, vai subindo o placar, batendo nos nomes que ele passou, e o nome é explodido (pode ser as letras e pontos espalhando, e se refazendo no slot de baixo), até ele chegar na colocação nova. Se ele for o primeiro, aparece um \"1ST PLACE!\" depois que ele ocupar o lugar dele, senão, acaba a animação. O score table tem que ser scrollable com as setas (adicione tb WASD como controle). Coloque SFXs para o placar tb. Depois da animação, vem as opções de play again ou main menu"

## Clarifications

### Session 2026-11-12

- Q: Qual o formato do nome? → A: Texto livre de até 10 caracteres (letras, números e espaço),
  digitado direto no teclado.
- Q: Quantas entradas o placar guarda e o que acontece com quem não entra? → A: As 10 melhores
  (estilo arcade); quem não entra vê o próprio resultado abaixo do placar, sem animação.
- Q: Em que telas o WASD funciona? → A: Em todo o jogo (partida, menus, Opções e placar), exceto
  na entrada de nome, onde as letras são digitadas.
- Q: O que acontece com "Opções" e "Quit" do menu de fim, agora substituído pelo placar? → A: O
  placar fica só com "Jogar de novo" e "Tela inicial"; a tela inicial ganha "Sair" (Jogar / Opções
  / Sair).
- Q: Quantas linhas o placar mostra de uma vez? → A: 5 linhas. O foguete começa no chão da lista
  visível e sobe na tela acelerando; um pouco acima do meio, a câmera passa a segui-lo (a lista
  desce e o foguete fica parado na tela, dando a sensação de que continua subindo); quando a 1ª
  posição já cabe na tela, a câmera para e o foguete segue subindo na tela com a velocidade máxima
  que atingiu no começo.
- Q: Com o placar cheio, o que acontece com o 10º colocado empurrado para fora? → A: Na ignição,
  ele explode (letras espalhando) e os pedaços caem para fora pela base do placar, com som de
  impacto; depois o foguete decola.
- Q: O mesmo nome pode aparecer mais de uma vez no placar? → A: Sim: cada partida é uma entrada
  separada (estilo arcade).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nome do jogador antes da partida (Priority: P1)

Ao escolher "Jogar" na tela inicial, o jogador digita seu nome e confirma; só então começa a
contagem e a partida. O nome é o que aparece no placar de highscore.

**Why this priority**: sem nome não há como identificar a pontuação no placar; é a base de todo o
resto.

**Independent Test**: abrir o jogo, escolher "Jogar", digitar um nome, confirmar e ver a contagem
começar.

**Acceptance Scenarios**:

1. **Given** a tela inicial, **When** o jogador confirma "Jogar", **Then** aparece a entrada de
   nome (com animação de entrada, como os outros painéis) em vez de ir direto para a contagem.
2. **Given** a entrada de nome, **When** o jogador digita letras e números, **Then** eles aparecem
   no campo, até o limite de caracteres (FR-002); Backspace apaga o último.
3. **Given** um nome válido digitado, **When** o jogador confirma com Enter, **Then** a entrada
   sai e começa a contagem "3, 2, 1".
4. **Given** o campo vazio, **When** o jogador aperta Enter, **Then** nada acontece (não há
   partida sem nome).
5. **Given** a entrada de nome, **When** o jogador aperta Esc, **Then** volta à tela inicial.
6. **Given** o jogador já jogou nesta sessão, **When** a entrada de nome abre de novo, **Then** o
   campo já vem com o último nome usado, pronto para confirmar ou editar.

---

### User Story 2 - Placar de highscore no fim da partida (Priority: P1)

Ao fim de cada partida (colisão, vitória ou tempo esgotado no Feeding Frenzy), em vez do menu de
fim atual, aparece um placar vertical (mais alto que largo) com posição, nome e pontos. A
pontuação da partida entra no placar na posição correta e fica salva para as próximas vezes.
Depois disso, o jogador escolhe "Jogar de novo" ou "Tela inicial". O placar pode ser rolado com
as setas ou WASD.

**Why this priority**: é o objetivo da feature: dar motivo para jogar de novo e comparar
resultados.

**Independent Test**: jogar duas partidas com nomes e pontuações diferentes, fechar e abrir o
jogo, e ver as duas no placar na ordem certa.

**Acceptance Scenarios**:

1. **Given** uma partida que terminou, **When** o jogo sai da tela da partida, **Then** aparece o
   placar vertical centralizado, com as entradas em ordem decrescente de pontos, cada uma com
   posição, nome e pontos.
2. **Given** a pontuação da partida se qualifica (FR-008), **When** o placar aparece, **Then** a
   entrada do jogador é inserida na posição correta e destacada.
3. **Given** dois resultados com a mesma pontuação, **When** são ordenados, **Then** o mais antigo
   fica acima.
4. **Given** o placar com mais entradas do que cabem na tela, **When** o jogador aperta ↑/↓ ou
   W/S, **Then** o placar rola uma linha por vez, sem passar do primeiro nem do último.
5. **Given** o placar já mostrado, **When** o jogador escolhe "Jogar de novo", **Then** começa a
   contagem de uma nova partida com o mesmo nome (sem pedir o nome outra vez).
6. **Given** o placar já mostrado, **When** o jogador escolhe "Tela inicial", **Then** volta para
   a tela inicial.
7. **Given** o jogo foi fechado e aberto, **When** o placar aparece, **Then** os resultados
   anteriores continuam lá.

---

### User Story 3 - Animação de foguete subindo o placar (Priority: P2)

Quando a pontuação entra no placar acima da última posição, o nome do jogador aparece na base com
partículas de foguete, treme no lugar e decola, subindo pelo placar. Cada nome que ele ultrapassa
"explode" (letras e pontos se espalham) e se remonta uma posição abaixo. Ao chegar na posição
nova, o nome pousa. Se for a primeira posição, aparece "1ST PLACE!"; depois disso surgem as
opções.

**Why this priority**: é o "juice" que transforma o placar numa recompensa; o placar funciona sem
ela.

**Independent Test**: com um placar já preenchido, fazer uma pontuação que suba algumas posições
e observar o tremor, a decolagem, as explosões e o pouso; repetir batendo o 1º lugar.

**Acceptance Scenarios**:

1. **Given** a pontuação entra no placar, **When** a animação começa, **Then** o nome do jogador
   aparece na base do placar com partículas de fogo saindo por baixo e treme no lugar por um
   instante (ignição).
2. **Given** a ignição terminou, **When** o foguete decola, **Then** o nome sobe na tela a partir
   do chão da lista visível, acelerando até a velocidade máxima; ao passar um pouco acima do meio
   da área visível, o nome fica parado na tela e a lista passa a descer na mesma velocidade
   (câmera seguindo o foguete).
3. **Given** a câmera seguindo o foguete, **When** a 1ª posição já cabe na tela, **Then** a lista
   para de descer e o nome volta a subir na tela, com a mesma velocidade máxima, até a sua
   posição.
4. **Given** o nome subindo, **When** ele alcança um nome que está acima, **Then** esse nome
   explode (letras e pontos se espalham), toca um som de impacto e o nome se remonta na posição
   logo abaixo.
5. **Given** o nome chega na sua nova posição, **When** pousa, **Then** as partículas param, toca
   um som de pouso e o nome fica destacado no lugar.
6. **Given** a nova posição é a primeira, **When** o nome pousa, **Then** aparece "1ST PLACE!" em
   destaque, com som de fanfarra, e só depois surgem as opções.
7. **Given** a nova posição não é a primeira, **When** o nome pousa, **Then** a animação termina e
   surgem as opções.
8. **Given** a animação em andamento, **When** o jogador aperta Enter, **Then** a animação pula
   para o fim (nome já no lugar, "1ST PLACE!" se for o caso) e as opções aparecem.

---

### User Story 4 - Sons do placar (Priority: P3)

O placar tem sons 8-bit próprios: digitar o nome, ignição, decolagem, impacto em cada nome
ultrapassado, pouso, fanfarra do 1º lugar e rolagem.

**Why this priority**: completa a sensação da animação; o placar funciona em silêncio.

**Independent Test**: digitar um nome e terminar uma partida que suba no placar, ouvindo cada som.

**Acceptance Scenarios**:

1. **Given** a entrada de nome, **When** o jogador digita ou apaga um caractere, **Then** toca um
   blip curto; tentar digitar além do limite não toca nada.
2. **Given** a animação do foguete, **When** acontecem ignição, decolagem, cada impacto e o pouso,
   **Then** cada momento tem seu som, no mesmo instante do efeito visual.
3. **Given** o 1º lugar, **When** "1ST PLACE!" aparece, **Then** toca uma fanfarra curta.
4. **Given** o placar parado, **When** o jogador rola e a posição muda, **Then** toca o som de
   navegação dos menus; no limite (sem mudança), não toca.

---

### Edge Cases

- Placar vazio (primeira partida de todas): a entrada vai direto para a 1ª posição; a animação
  ainda tem ignição e pouso, sem impactos, e mostra "1ST PLACE!".
- Pontuação que entra exatamente na última posição (ou num placar com espaço sobrando, abaixo de
  todos): ignição e pouso no lugar, sem subir; se o placar estava cheio, o antigo 10º ainda
  explode e cai para fora na ignição (FR-013a).
- Pontuação que não se qualifica (FR-008): o placar aparece sem animação de foguete, com o
  resultado do jogador mostrado à parte, abaixo do placar.
- Arquivo do placar ausente, corrompido ou com valores inválidos: o jogo abre com o placar vazio,
  sem erro; entradas inválidas são descartadas.
- Pontuação 0: é tratada como qualquer outra (entra se houver espaço ou se superar alguém).
- Nome com espaços nas pontas: espaços do começo e do fim são removidos ao confirmar; um nome só
  de espaços conta como vazio.
- Teclas de direção e WASD durante a animação: ignoradas (só Enter pula a animação).
- Esc no placar: equivale a "Tela inicial".
- Pausa (Esc) durante a partida continua igual; a entrada de nome não abre ao continuar.
- Fechar a janela no meio da animação: o resultado já foi salvo quando a partida terminou.

## Requirements *(mandatory)*

### Functional Requirements

**Nome**

- **FR-001**: Ao confirmar "Jogar" na tela inicial, o jogo DEVE mostrar a entrada de nome antes
  da contagem.
- **FR-002**: O nome DEVE aceitar até 10 caracteres entre letras, números e espaço, digitados
  livremente (outros caracteres são ignorados); Backspace apaga, Enter confirma, Esc volta à tela
  inicial; nome vazio não é aceito.
- **FR-003**: A entrada de nome DEVE vir preenchida com o último nome usado na sessão.
- **FR-004**: "Jogar de novo" NÃO DEVE pedir o nome outra vez.

**Placar**

- **FR-005**: Ao fim de toda partida (colisão, vitória ou tempo esgotado), o menu de fim atual
  DEVE ser substituído pelo placar de highscore.
- **FR-006**: O placar DEVE ser vertical (mais alto que largo), mostrar posição, nome e pontos, em
  ordem decrescente de pontos; empates ficam com o resultado mais antigo acima.
- **FR-007**: O placar DEVE ser salvo ao terminar cada partida e carregado ao abrir o jogo;
  arquivo ausente ou inválido resulta em placar vazio.
- **FR-008**: O placar DEVE guardar as 10 melhores entradas. Uma pontuação entra se o placar tem
  menos de 10 entradas ou se é maior que a da 10ª (que então sai). Quem não entra vê o próprio
  resultado (nome e pontos) abaixo do placar, sem animação de foguete. Cada partida é uma entrada
  separada: o mesmo nome pode aparecer várias vezes.
- **FR-009**: O placar DEVE mostrar 5 linhas por vez e rolar uma linha por vez com ↑/↓ e W/S,
  com uma indicação de que há mais conteúdo acima/abaixo.
- **FR-010**: Depois da animação, DEVEM aparecer as opções "Jogar de novo" e "Tela inicial",
  escolhidas com ←/→ ou A/D e confirmadas com Enter.
- **FR-010a**: A tela inicial DEVE ter as opções "Jogar", "Opções" e "Sair"; "Sair" fecha o jogo
  (com o som de confirmação, como o antigo "Quit").
- **FR-011**: O jogo DEVE aceitar W/A/S/D como alternativa a ↑/←/↓/→ em todas as telas
  (partida, tela inicial, pausa, Opções e placar), exceto na entrada de nome, onde as letras são
  digitadas.

**Animação**

- **FR-012**: Se a pontuação entra no placar, a animação DEVE mostrar o nome na base do placar
  com partículas de foguete, um tremor de ignição, a decolagem e a subida até a posição nova.
- **FR-013**: Cada nome ultrapassado DEVE explodir (letras e pontos espalhando) e se remontar uma
  posição abaixo.
- **FR-013a**: Se o placar estava cheio, o 10º colocado anterior DEVE explodir durante a ignição,
  com os pedaços caindo para fora pela base do placar e som de impacto, antes da decolagem.
- **FR-014**: Ao pousar na 1ª posição, DEVE aparecer "1ST PLACE!"; em outra posição, a animação
  termina no pouso.
- **FR-015**: Enter durante a animação DEVE pular para o estado final.
- **FR-016**: Durante a subida, o foguete DEVE partir do chão da lista visível e acelerar até uma
  velocidade máxima, mantida até o fim; quando ele passa um pouco acima do meio da área visível, a
  câmera o segue (a lista desce e ele fica parado na tela); quando a 1ª posição cabe na tela, a
  câmera para e ele termina a subida na tela. A rolagem automática termina com a posição do
  jogador visível.

**Som**

- **FR-017**: DEVEM existir sons 8-bit para: digitar/apagar no nome, ignição, decolagem, impacto
  em cada nome ultrapassado, pouso e fanfarra do 1º lugar; a rolagem usa o som de navegação
  existente; todos respeitam o volume de Efeitos.

### Key Entities

- **Entrada do placar**: nome, pontos e ordem de chegada (para desempate).
- **Placar**: lista ordenada das 10 melhores entradas (FR-008), salva entre sessões.
- **Nome do jogador**: texto digitado na entrada de nome, lembrado durante a sessão.
- **Animação do foguete**: posição de partida, posição de chegada, nomes ultrapassados e etapa
  atual (ignição, subida, pouso, "1ST PLACE!").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Da confirmação de "Jogar" ao começo da contagem, o jogador leva no máximo uma tela
  (entrada de nome) e uma tecla se o nome já estiver preenchido.
- **SC-002**: 100% das partidas terminadas aparecem no placar na posição correta (quando se
  qualificam) e continuam lá após fechar e abrir o jogo.
- **SC-003**: A animação completa dura no máximo 5 s, mesmo subindo dezenas de posições, e pode
  ser pulada a qualquer momento.
- **SC-004**: Durante a animação do placar, o jogo mantém 60 quadros por segundo.
- **SC-005**: Um arquivo de placar corrompido nunca impede o jogo de abrir.

## Assumptions

- "Play again" e "main menu" aparecem em português como "Jogar de novo" e "Tela inicial", no
  padrão dos menus atuais; "1ST PLACE!" fica em inglês, como pedido.
- O placar substitui o menu de fim de partida (Restart/Opções/Quit); Opções continua acessível
  pela tela inicial e pela pausa, e "Sair" passa para a tela inicial (FR-010a).
- O jingle de derrota/vitória e o tremor de colisão continuam acontecendo antes do placar.
- O placar fica salvo junto com as configurações (pasta de configuração do usuário).
- A velocidade máxima do foguete é escolhida para que a subida mais longa possível (da 10ª à 1ª
  posição) caiba no limite de 5 s da animação (SC-003).
- Sem animação (pontuação que não entra), o placar abre rolado até o fim, mostrando as últimas
  posições logo acima do resultado do jogador.
- O nome do jogador é lembrado só durante a sessão; ao abrir o jogo, o campo começa vazio.
