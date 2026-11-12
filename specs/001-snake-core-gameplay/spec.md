# Feature Specification: Núcleo do Snake — movimento, comida e pontuação

**Feature Branch**: `001-snake-core-gameplay`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "Build the core Snake movement, food spawning, and score tracking"

## Clarifications

### Session 2026-11-12

- Q: O que deve acontecer quando a cabeça da cobra bate na borda da grade ou no próprio corpo? → A: Game over na parede e no corpo; a partida termina e mostra a pontuação final.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mover a cobra pela grade (Priority: P1)

O jogador inicia uma partida e vê a cobra se movendo sozinha, uma casa por passo, na direção
atual. Com as setas do teclado, o jogador muda a direção da cobra.

**Why this priority**: sem movimento controlável não existe jogo; é a menor fatia jogável.

**Independent Test**: iniciar a partida, observar a cobra avançar uma casa por passo e trocar a
direção com as setas. Entrega valor sozinha como "cobra controlável na tela".

**Acceptance Scenarios**:

1. **Given** uma partida recém-iniciada, **When** passa um passo de jogo sem nenhuma tecla,
   **Then** a cobra avança exatamente uma casa na direção inicial e mantém o mesmo comprimento.
2. **Given** a cobra indo para a direita, **When** o jogador pressiona "para cima",
   **Then** no passo seguinte a cobra avança uma casa para cima.
3. **Given** a cobra indo para a direita com comprimento maior que 1, **When** o jogador
   pressiona "para a esquerda" (direção oposta), **Then** o comando é ignorado e a cobra
   continua para a direita.
4. **Given** o jogador pressiona duas direções dentro do mesmo passo, **When** o passo é
   processado, **Then** apenas uma mudança de direção é aplicada por passo, e a cobra nunca
   inverte sobre si mesma.
5. **Given** a cobra com a cabeça na borda e indo em direção a ela, **When** o próximo passo
   acontece, **Then** a partida termina e a pontuação final é exibida.
6. **Given** a cobra prestes a entrar em uma casa do próprio corpo, **When** o próximo passo
   acontece, **Then** a partida termina e a pontuação final é exibida.

---

### User Story 2 - Comer a comida e crescer (Priority: P2)

Há sempre uma comida na grade. Quando a cabeça da cobra chega à casa da comida, a cobra cresce e
uma nova comida aparece em uma casa livre.

**Why this priority**: crescer é o objetivo do jogo e o que dá desafio ao movimento.

**Independent Test**: guiar a cobra até a comida e verificar que ela cresce uma casa e que outra
comida surge em casa não ocupada pela cobra.

**Acceptance Scenarios**:

1. **Given** uma partida em andamento, **When** a grade é exibida, **Then** existe exatamente
   uma comida, em uma casa não ocupada pela cobra.
2. **Given** a comida na casa imediatamente à frente da cabeça, **When** a cobra avança,
   **Then** o comprimento da cobra aumenta em 1.
3. **Given** a cobra acabou de comer, **When** a nova comida é gerada, **Then** ela aparece
   em uma casa livre (nunca sobre a cobra).
4. **Given** a mesma semente de aleatoriedade e a mesma sequência de comandos, **When** duas
   partidas são jogadas, **Then** as comidas aparecem nas mesmas casas, na mesma ordem.

---

### User Story 3 - Acompanhar a pontuação (Priority: P3)

O jogador vê a pontuação da partida, que aumenta a cada comida.

**Why this priority**: dá feedback de progresso, mas o jogo já funciona sem ela.

**Independent Test**: comer comidas e verificar que a pontuação exibida acompanha a quantidade
de comidas comidas.

**Acceptance Scenarios**:

1. **Given** uma partida recém-iniciada, **When** a pontuação é exibida, **Then** ela é 0.
2. **Given** a pontuação atual P, **When** a cobra come uma comida, **Then** a pontuação passa
   a ser P + 1.
3. **Given** a cobra se move sem comer, **When** passos de jogo acontecem, **Then** a
   pontuação não muda.

---

### Edge Cases

- **Colisão com a parede**: se a cabeça tentaria sair da grade, a partida termina (game over)
  e a pontuação final é exibida; a cobra não avança para fora da grade.
- **Colisão com o próprio corpo**: se a cabeça entraria em uma casa ocupada pelo corpo, a
  partida termina (game over) e a pontuação final é exibida.
- **Depois do game over**: nenhum passo de jogo ou comando altera mais o estado da partida.
- **Mover para a casa que a cauda acabou de liberar**: permitido, pois a cauda se desloca no
  mesmo passo (desde que a cobra não esteja crescendo nesse passo).
- **Grade cheia**: se a cobra ocupar todas as casas e não houver casa livre para a comida, a
  partida termina com vitória.
- **Comando oposto à direção atual**: ignorado (ver User Story 1, cenário 3).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O jogo DEVE representar o campo como uma grade retangular de casas de tamanho fixo
  durante a partida.
- **FR-002**: A cobra DEVE começar com comprimento 3, no centro da grade, movendo-se para a
  direita.
- **FR-003**: A cada passo de jogo, a cobra DEVE avançar exatamente uma casa na direção atual.
- **FR-004**: O jogador DEVE poder mudar a direção da cobra para cima, baixo, esquerda e
  direita; comandos para a direção oposta à atual DEVEM ser ignorados.
- **FR-005**: No máximo uma mudança de direção DEVE ser aplicada por passo de jogo.
- **FR-006**: Sempre que a partida estiver em andamento, DEVE haver exatamente uma comida na
  grade, em uma casa não ocupada pela cobra.
- **FR-007**: Quando a cabeça entra na casa da comida, a cobra DEVE crescer 1 casa e uma nova
  comida DEVE ser gerada em uma casa livre escolhida aleatoriamente.
- **FR-008**: A escolha da casa da comida DEVE ser reproduzível: com a mesma semente e a mesma
  sequência de comandos, as comidas DEVEM surgir nas mesmas casas.
- **FR-009**: A pontuação DEVE começar em 0 e aumentar 1 ponto por comida comida.
- **FR-010**: A pontuação atual DEVE ficar visível durante toda a partida.
- **FR-011**: Se o próximo passo levaria a cabeça para fora da grade ou para uma casa ocupada
  pelo corpo, a partida DEVE terminar (game over) e a pontuação final DEVE ser exibida.
- **FR-013**: Após o fim da partida (game over ou vitória), passos de jogo e comandos de
  direção NÃO DEVEM alterar o estado da partida.
- **FR-012**: Se não houver casa livre para a comida, a partida DEVE terminar com vitória.

### Key Entities *(include if feature involves data)*

- **Grade**: o campo de jogo; largura e altura em casas.
- **Cobra**: sequência ordenada de casas (cabeça primeiro) e direção atual.
- **Comida**: uma casa da grade que, ao ser alcançada pela cabeça, faz a cobra crescer.
- **Partida**: estado completo do jogo em um instante — grade, cobra, comida, pontuação e
  situação (em andamento, encerrada).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um jogador novo consegue mover a cobra e comer a primeira comida em menos de
  30 segundos após iniciar a partida, sem instruções.
- **SC-002**: Em 100% dos passos de uma partida, existe exatamente uma comida e ela nunca está
  sobre a cobra.
- **SC-003**: A pontuação exibida é igual ao número de comidas comidas em 100% das partidas
  testadas.
- **SC-004**: Duas partidas com a mesma semente e a mesma sequência de comandos produzem
  exatamente a mesma sequência de estados.
- **SC-005**: A cobra responde a uma mudança de direção no passo seguinte ao comando, sem atraso
  perceptível para o jogador.

## Assumptions

- Grade padrão de 20 × 20 casas.
- Velocidade constante nesta feature (um passo de jogo em intervalo fixo); aceleração
  progressiva fica para uma feature futura.
- Jogo para um jogador, local, controlado por teclado (setas).
- Pontuação apenas da partida atual; recorde (high score) persistente está fora do escopo.
- Telas de menu, pausa e reinício estão fora do escopo; ao fim da partida o jogador fecha a
  janela e abre de novo para jogar outra vez.
