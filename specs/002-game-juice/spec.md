# Feature Specification: Game juice — feedback visual do Snake

**Feature Branch**: `002-game-juice`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "game juice - vamos adicionar particulas na ponta da cobra ao colher frutas, adicionar uma animação de pulse no score com flash de cor no número, camera shake ao colidir e ter game over, animação de entrada e saida da UI, tanto no início do jogo, como na janela de end game"

## Clarifications

### Session 2026-11-12

- Q: O que aparece na tela por trás da tela inicial e durante a contagem regressiva: o tabuleiro com a cobra parada e a comida, ou um fundo vazio? → A: Tabuleiro sempre visível: escurecido atrás da tela inicial; na contagem, cobra parada e comida já posicionada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recompensa visual ao comer (Priority: P1)

Quando a cobra come uma fruta, o jogador vê uma explosão de partículas saindo da cabeça da
cobra e o número da pontuação pulsa com um flash de cor.

**Why this priority**: comer é a ação mais frequente e positiva do jogo; reforçá-la é o que
mais aumenta a sensação de recompensa.

**Independent Test**: comer uma fruta e observar as partículas na cabeça e o pulso com flash no
placar. Entrega valor sozinha, sem depender das outras histórias.

**Acceptance Scenarios**:

1. **Given** uma partida em andamento, **When** a cobra come uma fruta, **Then** surgem
   partículas na posição da cabeça, que se espalham e desaparecem em até 0,6 s.
2. **Given** uma partida em andamento, **When** a cobra come uma fruta, **Then** o número da
   pontuação aumenta de tamanho e volta ao normal (pulso) em até 0,3 s, mudando de cor durante
   o pulso e voltando à cor original ao final.
3. **Given** a cobra come duas frutas em sequência rápida, **When** o segundo efeito começa
   antes do primeiro terminar, **Then** os dois conjuntos de partículas aparecem e o pulso do
   placar reinicia, sem travar o jogo.
4. **Given** uma partida em andamento, **When** a cobra anda sem comer, **Then** não surgem
   partículas e o placar não pulsa.

---

### User Story 2 - Impacto ao colidir (Priority: P2)

Quando a cobra bate na parede ou no próprio corpo, a tela treme brevemente antes de a partida
ser encerrada.

**Why this priority**: dá peso ao momento da derrota e deixa claro o que aconteceu, mas acontece
uma vez por partida.

**Independent Test**: bater na parede e observar a tela tremer antes de o menu de fim de partida
aparecer.

**Acceptance Scenarios**:

1. **Given** uma partida em andamento, **When** a cobra bate na parede ou no próprio corpo,
   **Then** toda a área de jogo treme por até 0,4 s, com intensidade que diminui até parar.
2. **Given** o tremor de colisão terminou, **When** a tela se estabiliza, **Then** a área de
   jogo volta exatamente à posição original e o menu de fim de partida aparece.
3. **Given** a partida termina por vitória (grade cheia), **When** o fim é detectado,
   **Then** a tela não treme.

---

### User Story 3 - Entrada e saída da interface (Priority: P3)

Os elementos de interface entram e saem da tela com animação: no início da partida e na janela
de fim de partida.

**Why this priority**: deixa o jogo mais polido, mas não afeta a jogabilidade.

**Independent Test**: iniciar o jogo, perder, escolher "Restart" e observar as animações de
entrada e saída em cada transição.

**Acceptance Scenarios**:

1. **Given** o jogo acabou de abrir, **When** a primeira tela aparece, **Then** surge uma tela
   inicial com o título "Snake" e a instrução "Pressione Espaço para começar", entrando com
   animação de até 0,4 s, sobre o tabuleiro escurecido (cobra na posição inicial e comida já
   posicionada); a cobra ainda não anda.
2. **Given** a tela inicial visível, **When** o jogador pressiona Espaço ou Enter, **Then** a
   tela inicial sai com animação de até 0,4 s e começa a contagem regressiva.
3. **Given** a contagem regressiva começou, **When** ela avança, **Then** os números "3", "2" e
   "1" aparecem animados no centro, um por segundo, sobre o tabuleiro visível com a cobra parada
   e a comida já no lugar; o placar entra com animação, e só depois do "1" a cobra começa a
   andar.
4. **Given** a contagem regressiva em andamento, **When** o jogador pressiona as setas, Espaço
   ou Enter, **Then** nada acontece (a cobra só aceita comandos depois da contagem).
5. **Given** a partida terminou, **When** a janela de fim de partida aparece, **Then** ela entra
   com animação de até 0,4 s (por exemplo, surgindo e crescendo a partir do centro, com o fundo
   escurecendo gradualmente).
6. **Given** a janela de fim de partida está visível, **When** o jogador confirma "Restart",
   **Then** a janela sai com animação de até 0,4 s e começa a contagem regressiva da nova
   partida (sem voltar à tela inicial).
7. **Given** a janela de fim de partida está entrando, **When** o jogador pressiona ↑, ↓,
   Espaço ou Enter, **Then** a animação de entrada é concluída imediatamente e a tecla é
   tratada normalmente.

---

### Edge Cases

- **Efeitos durante a pausa do fim de partida**: partículas e pulso que estavam em andamento
  quando a cobra colide terminam normalmente (não congelam no meio).
- **Comer e colidir no mesmo instante**: não acontece pelas regras atuais (comer não causa
  colisão), mas se a última fruta der vitória, há partículas e pulso, sem tremor.
- **Fechar a janela na tela inicial ou durante a contagem**: o jogo fecha imediatamente.
- **Quit durante a animação de saída**: escolher "Quit" fecha o jogo sem esperar animação.
- **Reinício rápido**: confirmar "Restart" várias vezes seguidas não acumula animações; só a
  primeira confirmação conta.
- **Efeitos não alteram regras**: nenhuma animação muda a posição da cobra, da comida, a
  pontuação ou o ritmo dos passos de jogo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Ao comer uma fruta, o jogo DEVE emitir partículas a partir da posição da cabeça da
  cobra, que se espalham e somem em até 0,6 s.
- **FR-002**: Ao comer uma fruta, o número da pontuação DEVE pulsar (aumentar e voltar ao tamanho
  normal) em até 0,3 s, com um flash de cor que volta à cor original ao final.
- **FR-003**: Se um novo efeito de comer começar antes do anterior terminar, as partículas DEVEM
  coexistir e o pulso do placar DEVE reiniciar.
- **FR-004**: Ao colidir com a parede ou com o próprio corpo, a área de jogo DEVE tremer por até
  0,4 s, com intensidade decrescente, e voltar exatamente à posição original.
- **FR-005**: A vitória (grade cheia) NÃO DEVE causar tremor.
- **FR-006**: A janela de fim de partida DEVE aparecer só depois que o tremor de colisão
  terminar.
- **FR-007**: Ao abrir o jogo, DEVE ser exibida uma tela inicial com o título "Snake" e a
  instrução "Pressione Espaço para começar", com animação de entrada de até 0,4 s, sobre o
  tabuleiro da partida escurecido (cobra parada na posição inicial e comida posicionada); Espaço
  ou Enter DEVEM fechá-la com animação de saída de até 0,4 s.
- **FR-012**: Antes de toda partida (depois da tela inicial e depois de cada "Restart"), DEVE
  haver uma contagem regressiva animada "3", "2", "1", um número por segundo, enquanto o placar
  entra com animação; durante a contagem o tabuleiro fica visível com a cobra parada e a comida
  já posicionada, e a cobra só começa a andar depois do "1".
- **FR-013**: Durante a contagem regressiva, setas, Espaço e Enter NÃO DEVEM ter efeito.
- **FR-008**: A janela de fim de partida DEVE entrar com animação de até 0,4 s e, ao confirmar
  "Restart", sair com animação de até 0,4 s antes da nova partida.
- **FR-009**: Qualquer tecla do menu pressionada durante a animação de entrada da janela DEVE
  concluir a animação imediatamente e ser tratada normalmente; "Quit" DEVE fechar o jogo sem
  esperar animação.
- **FR-010**: Nenhum efeito visual PODE alterar o estado ou as regras da partida (posição da
  cobra e da comida, pontuação, situação da partida, ritmo dos passos).
- **FR-011**: Os efeitos DEVEM ser determinísticos para a mesma seed e a mesma sequência de
  comandos (mesmas partículas, mesmo tremor), seguindo a constituição.

### Key Entities *(include if feature involves data)*

- **Efeito de partículas**: origem (casa da cabeça no momento em que comeu), conjunto de
  partículas com direção, velocidade e tempo de vida.
- **Pulso do placar**: tempo decorrido desde a última fruta; define escala e cor do número.
- **Tremor de tela**: tempo decorrido e intensidade atual; define o deslocamento da área de jogo.
- **Animação de UI**: elemento animado, tipo (entrada ou saída), duração e progresso.
- **Fase da tela**: em qual momento o jogo está — tela inicial, contagem regressiva, partida em
  andamento ou fim de partida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das frutas comidas, partículas e pulso do placar aparecem e terminam dentro
  dos tempos definidos (0,6 s e 0,3 s).
- **SC-002**: Em 100% das colisões, o tremor dura no máximo 0,4 s e a área de jogo volta à
  posição original; em 0% das vitórias há tremor.
- **SC-003**: Toda transição de interface (entrada e saída) leva no máximo 0,4 s; entre
  confirmar "Restart" e a cobra começar a andar passam no máximo 3,4 s (saída da janela +
  contagem de 3 s).
- **SC-004**: Com os efeitos ativos, incluindo três explosões de partículas simultâneas, a
  animação continua a 60 quadros por segundo, como antes desta feature.
- **SC-005**: Com a mesma seed e os mesmos comandos, duas sessões produzem exatamente o mesmo
  estado de jogo que antes desta feature (os efeitos não mudam o resultado).

## Assumptions

- Os efeitos são sempre ativos; uma opção para desligá-los (acessibilidade, ex.: tremor e
  flashes) fica para uma feature futura. Intensidades são moderadas para não incomodar.
- Sem efeitos sonoros nesta feature; apenas feedback visual.
- O ritmo do jogo (8 passos por segundo) não muda; o fim de partida já interrompe os passos, então
  o tremor acontece com a cobra parada.
- As regras da feature 001 (movimento, comida, colisão, pontuação, menu) continuam iguais,
  exceto o início automático da partida, que passa a ser precedido pela tela inicial (só ao abrir
  o jogo) e pela contagem regressiva (em toda partida).
- A tela inicial aparece apenas ao abrir o jogo; "Restart" leva direto à contagem regressiva.
