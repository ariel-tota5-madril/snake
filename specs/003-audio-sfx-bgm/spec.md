# Feature Specification: Áudio — efeitos sonoros e música 8-bit

**Feature Branch**: `003-audio-sfx-bgm`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "SFX e BGM - quero que vc crie músicas e sfx estilo 8bit, upbeat. Crie sfx para o movimento da cobra (algo mais suave pra nao ficar mto obnoxious), coleta, animacao de punch do score, crash da cobra na parede ou nela mesma, e qualquer outro evento importante que vc encontre"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sons da jogabilidade (Priority: P1)

Durante a partida, cada ação importante tem um som 8-bit: um tique suave a cada passo da cobra,
um som de coleta ao comer, um "pop" no momento em que o placar dá o salto, e um som de batida
quando a cobra colide.

**Why this priority**: o som da ação é o que mais reforça o feedback do jogo e complementa os
efeitos visuais da feature 002.

**Independent Test**: jogar uma partida, comer frutas e bater na parede, ouvindo cada som no
momento certo.

**Acceptance Scenarios**:

1. **Given** uma partida em andamento, **When** a cobra avança uma casa, **Then** toca um tique
   curto e suave, mais baixo que todos os outros efeitos, sem cansar o ouvido em partidas longas.
2. **Given** uma partida em andamento, **When** a cobra come uma fruta, **Then** toca um som de
   coleta curto e ascendente, no mesmo instante em que as partículas surgem.
3. **Given** a cobra acabou de comer, **When** o placar atinge o pico do pulso, **Then** toca um
   "pop" curto, distinto do som de coleta, sincronizado com o salto do número.
4. **Given** uma partida em andamento, **When** a cobra bate na parede ou no próprio corpo,
   **Then** toca um som de batida (ruidoso e descendente) junto com o tremor de tela.
5. **Given** a cobra come no mesmo passo em que avança, **When** os sons tocam, **Then** o som de
   coleta é ouvido claramente por cima do tique de movimento.

---

### User Story 2 - Música de fundo (Priority: P2)

O jogo tem música 8-bit animada (upbeat) em loop: uma faixa na tela inicial e outra durante a
partida.

**Why this priority**: dá identidade e ritmo ao jogo, mas não interfere na jogabilidade.

**Independent Test**: abrir o jogo e ouvir a música da tela inicial; começar a partida e ouvir a
música de jogo; perder e notar a música mudar.

**Acceptance Scenarios**:

1. **Given** o jogo acabou de abrir, **When** a tela inicial aparece, **Then** começa a tocar a
   música da tela inicial, em loop sem cortes audíveis.
2. **Given** a contagem regressiva terminou, **When** a cobra começa a andar, **Then** começa a
   música de partida, em loop sem cortes audíveis.
3. **Given** a música de partida tocando, **When** a partida termina (colisão ou vitória),
   **Then** a música de partida para e toca o jingle correspondente (derrota ou vitória).
4. **Given** a música tocando, **When** qualquer efeito sonoro toca, **Then** o efeito é
   claramente audível por cima da música (a música fica em volume mais baixo que os efeitos).

---

### User Story 3 - Sons de interface e transições (Priority: P3)

As telas e o menu têm sons próprios: bipes da contagem regressiva, sons de navegação e de
confirmação no menu e na tela inicial, e jingles de fim de partida.

**Why this priority**: completa o polimento sonoro, mas é o menos frequente.

**Independent Test**: começar o jogo pela tela inicial, ouvir a contagem, perder, navegar no
menu e confirmar.

**Acceptance Scenarios**:

1. **Given** a tela inicial, **When** o jogador pressiona Espaço ou Enter, **Then** toca um som
   de confirmação.
2. **Given** a contagem regressiva, **When** aparecem "3", "2" e "1", **Then** toca um bipe a
   cada número, e um bipe mais agudo e mais longo quando a cobra começa a andar ("vai!").
3. **Given** o menu de fim de partida, **When** o jogador move a seleção com ↑/↓, **Then** toca
   um bipe curto de navegação; se a seleção não mudar (já está na ponta), nenhum som toca.
4. **Given** o menu de fim de partida, **When** o jogador confirma "Restart" ou "Quit",
   **Then** toca o som de confirmação ("Quit" toca o som antes de o jogo fechar, sem atrasar o
   fechamento em mais de 0,3 s).
5. **Given** a partida terminou por colisão, **When** a janela de fim de partida entra,
   **Then** toca um jingle curto de derrota; se terminou por vitória, um jingle curto de vitória.

---

### User Story 4 - Pausa e opções de áudio (Priority: P2)

O jogador pode pausar a partida com Esc e ajustar o volume da música e dos efeitos numa tela de
Opções, acessível pela tela inicial, pela pausa e pelo menu de fim de partida.

**Why this priority**: com áudio no jogo, o jogador precisa poder abaixar ou silenciar o som; a
pausa permite fazer isso (e interromper o jogo) sem perder a partida.

**Independent Test**: durante a partida, pressionar Esc, abrir Opções, mudar os volumes, voltar
e continuar a partida do mesmo ponto.

**Acceptance Scenarios**:

1. **Given** uma partida em andamento, **When** o jogador pressiona Esc, **Then** a partida
   congela (cobra, comida, pontuação e efeitos param) e aparece o menu de pausa com "Continuar",
   "Opções" e "Sair", com "Continuar" selecionado; a música de partida fica em volume reduzido.
2. **Given** o menu de pausa, **When** o jogador escolhe "Continuar" ou pressiona Esc,
   **Then** o menu fecha e a partida continua exatamente de onde parou.
3. **Given** a tela inicial, **When** ela aparece, **Then** mostra um menu com "Jogar" e
   "Opções" (com "Jogar" selecionado), no lugar da instrução "Pressione Espaço para começar".
4. **Given** a tela inicial, o menu de pausa ou o menu de fim de partida, **When** o jogador
   escolhe "Opções", **Then** abre a tela de Opções com os sliders "Música" e "Efeitos" e o item
   "Voltar".
5. **Given** a tela de Opções com um slider selecionado, **When** o jogador pressiona ← ou →,
   **Then** o volume diminui ou aumenta 10% (entre 0% e 100%), a barra do slider reflete o novo
   valor e a mudança vale imediatamente; ao mexer em "Efeitos", toca um som de amostra no novo
   volume.
6. **Given** a tela de Opções, **When** o jogador escolhe "Voltar" ou pressiona Esc, **Then**
   volta para a tela de onde veio (tela inicial, pausa ou fim de partida), no mesmo estado.
7. **Given** um volume em 0%, **When** o som correspondente deveria tocar, **Then** nada é
   ouvido (0% equivale a mudo).
8. **Given** o menu de pausa, **When** o jogador escolhe "Sair", **Then** o jogo fecha.

---

### Edge Cases

- **Muitos sons ao mesmo tempo** (comer + pulso + tique no mesmo instante): todos tocam, sem
  cortar uns aos outros nem estourar o volume.
- **Teclas ignoradas** (setas na tela inicial, qualquer tecla durante a contagem ou o tremor):
  não tocam som.
- **Comando de direção na partida**: não tem som próprio (o tique de movimento já marca o ritmo).
- **Restart várias vezes seguidas**: o som de confirmação toca uma vez só, como a ação.
- **Sistema sem saída de áudio**: o jogo abre e funciona normalmente, apenas em silêncio.
- **Esc fora da partida**: na tela inicial, na contagem, no tremor e no fim de partida, Esc não
  pausa (só a tela de Opções e a pausa reagem ao Esc, para voltar).
- **Pausa congela o tempo**: enquanto pausado, nada do jogo avança (passos, partículas, pulso,
  tremor); ao continuar, a cobra retoma o ritmo normal, sem dar passos acumulados.
- **Sliders nas pontas**: ← em 0% e → em 100% não mudam o valor nem tocam o bipe de navegação.
- **Sons não alteram o jogo**: nenhum som muda a posição da cobra, da comida, a pontuação, as
  fases de tela ou o ritmo dos passos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Todo áudio (efeitos e músicas) DEVE ter estilo 8-bit (sons de ondas simples, como
  consoles clássicos) e ser criado pelo próprio projeto, sem usar arquivos de terceiros.
- **FR-002**: A cada passo da cobra, DEVE tocar um tique curto e suave, com o menor volume entre
  todos os efeitos.
- **FR-003**: Ao comer uma fruta, DEVE tocar um som de coleta curto e ascendente, no mesmo
  instante em que as partículas surgem.
- **FR-004**: No pico do pulso do placar (60 ms após comer), DEVE tocar um "pop" curto e distinto
  do som de coleta.
- **FR-005**: Na colisão com a parede ou com o próprio corpo, DEVE tocar um som de batida junto
  com o início do tremor de tela.
- **FR-006**: O jogo DEVE ter uma música em loop na tela inicial e outra música em loop durante a
  partida, ambas 8-bit e animadas (upbeat), sem cortes audíveis na volta do loop.
- **FR-007**: A música de partida DEVE começar quando a cobra começa a andar e parar quando a
  partida termina; nesse momento DEVE tocar um jingle curto de derrota (colisão) ou de vitória
  (grade cheia).
- **FR-008**: A contagem regressiva DEVE tocar um bipe em cada número ("3", "2", "1") e um bipe
  diferente (mais agudo e mais longo) quando a cobra começa a andar.
- **FR-009**: Confirmar na tela inicial e no menu DEVE tocar um som de confirmação; mover a
  seleção do menu DEVE tocar um bipe de navegação apenas quando a seleção mudar.
- **FR-010**: Teclas ignoradas pelo jogo NÃO DEVEM tocar som.
- **FR-011**: A música DEVE tocar em volume menor que os efeitos, de modo que todo efeito seja
  audível por cima dela.
- **FR-012**: Vários sons simultâneos DEVEM tocar juntos sem se cortarem.
- **FR-013**: Se o sistema não tiver saída de áudio, o jogo DEVE funcionar normalmente, em
  silêncio.
- **FR-014**: Nenhum som PODE alterar o estado ou as regras da partida nem o fluxo de telas.
- **FR-015**: Durante a partida, Esc DEVE pausar o jogo: tudo congela e aparece o menu de pausa
  ("Continuar", "Opções", "Sair"); "Continuar" ou Esc retomam a partida exatamente do ponto em
  que parou; "Sair" fecha o jogo. Durante a pausa, a música de partida DEVE ficar em volume
  reduzido.
- **FR-016**: A tela inicial DEVE apresentar um menu com "Jogar" e "Opções" no lugar da instrução
  "Pressione Espaço para começar"; o menu de fim de partida DEVE passar a ter "Restart",
  "Opções" e "Quit".
- **FR-017**: A tela de Opções DEVE ser acessível pela tela inicial, pela pausa e pelo menu de fim
  de partida, e DEVE ter os sliders "Música" e "Efeitos" (0% a 100%, passos de 10%, ajustados
  com ← e →) e o item "Voltar"; "Voltar" ou Esc retornam à tela de origem no mesmo estado.
- **FR-018**: Mudanças de volume DEVEM valer imediatamente; 0% DEVE silenciar o tipo de som
  correspondente; ajustar "Efeitos" DEVE tocar um som de amostra no novo volume.
- **FR-019**: Os volumes escolhidos DEVEM continuar valendo ao reiniciar a partida, enquanto o
  jogo estiver aberto.

### Key Entities *(include if feature involves data)*

- **Evento sonoro**: momento do jogo que dispara um efeito (passo, coleta, pico do pulso,
  colisão, número da contagem, início da partida, navegação, confirmação, fim de partida).
- **Efeito sonoro (SFX)**: som curto associado a um evento, com volume relativo.
- **Faixa de música (BGM)**: música em loop associada a uma tela (tela inicial, partida).
- **Jingle**: música curta, sem loop, tocada no fim da partida (derrota ou vitória).
- **Configuração de áudio**: volume da música e volume dos efeitos (0% a 100%).
- **Menu**: lista de opções com uma selecionada (tela inicial, pausa, fim de partida, Opções).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos eventos listados nos requisitos tocam o som correspondente, com atraso
  máximo de 50 ms em relação ao evento visual.
- **SC-002**: O tique de movimento é o efeito de menor volume; numa partida de 2 minutos, o
  jogador consegue ouvir os outros efeitos claramente por cima dele.
- **SC-003**: As músicas repetem em loop sem pausa ou estalo audível na emenda.
- **SC-004**: Com áudio ativo, o jogo mantém 60 quadros por segundo.
- **SC-005**: Em uma máquina sem dispositivo de áudio, o jogo abre e completa uma partida sem
  erros.

## Assumptions

- Os sons são sintetizados pelo próprio projeto no estilo 8-bit (ondas quadrada, triangular e
  ruído), garantindo originalidade e ausência de licenças de terceiros.
- Músicas curtas (loops de alguns segundos a poucos compassos), adequadas a um jogo casual.
- Mudar de direção não tem som próprio, para não poluir (o tique de movimento já dá o ritmo).
- As animações de entrada e saída de interface não ganham som próprio, para não sobrepor os sons
  de confirmação e os jingles.
- Volumes iniciais: Música 60%, Efeitos 80%; valem só enquanto o jogo está aberto (guardar
  entre sessões fica para uma feature futura).
- O menu de pausa e a tela de Opções usam as mesmas animações de entrada e saída e os mesmos
  sons de navegação e confirmação dos outros menus.
- As regras das features 001 e 002 continuam iguais. Mudam apenas as telas: a tela inicial
  ganha o menu "Jogar"/"Opções", o menu de fim de partida ganha "Opções" e passa a existir a
  pausa (Esc).
