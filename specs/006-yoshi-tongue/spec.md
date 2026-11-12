# Feature Specification: Língua de Yoshi — habilidade com cooldown

**Feature Branch**: `006-yoshi-tongue`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "Fazer um botão com um coodown de \"lingua de yoshi\" que pode atirar a lingua pra frente e comer a fruta sem ter chegado nela. Eh necessario um icone com um timer (highlight em formato de relógio na textura, e não um timer de número), com um efeito de pulse e sfx quando o timer acaba e pode usar novamente. Mantenha o botão pulsando e brilhando levemente pra ver com visão periferica que está disponível"

## Clarifications

### Session 2026-11-12

- Q: Qual o alcance da língua? → A: 3 casas à frente da cabeça.
- Q: Quanto tempo de recarga? → A: 8 s.
- Q: A língua funciona no Feeding Frenzy? → A: Não: durante o Frenzy a língua fica bloqueada e o
  ícone aparece acinzentado.
- Q: Errar o disparo também gasta a recarga? → A: Sim: todo disparo, acertando ou não, gasta a
  recarga inteira de 8 s.
- Q: Qual tecla dispara a língua? → A: Espaço.
- Q: Onde fica o ícone da língua? → A: Canto inferior esquerdo, fixo, com cerca de duas casas de
  tamanho.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Atirar a língua e comer à distância (Priority: P1)

Durante a partida, o jogador aperta o botão da língua: a cobra dispara a língua em linha reta, na
direção em que está andando. Se a fruta estiver ao alcance nessa linha, ela é puxada e comida como
se a cobra tivesse chegado nela. Depois de usar, a língua entra em recarga.

**Why this priority**: é a mecânica nova; sem ela, o resto (ícone, sons) não tem função.

**Independent Test**: alinhar a cobra com a fruta a algumas casas de distância, apertar o botão e
ver a fruta ser comida sem a cobra chegar nela; apertar de novo logo depois e nada acontecer.

**Acceptance Scenarios**:

1. **Given** a língua disponível e a fruta na mesma linha à frente da cabeça, dentro do alcance
   (FR-003), **When** o jogador aperta o botão, **Then** a língua se estica até a fruta, a puxa de
   volta e a fruta é comida: o placar sobe, a cobra cresce e os efeitos de coleta acontecem, como
   numa coleta normal.
2. **Given** a língua disponível e nenhuma fruta ao alcance na linha à frente, **When** o jogador
   aperta o botão, **Then** a língua se estica até o alcance máximo (ou até bater na parede ou no
   corpo), volta vazia e a recarga de 8 s começa do mesmo jeito.
3. **Given** a língua foi usada, **When** o jogador aperta o botão de novo durante a recarga,
   **Then** nada acontece.
4. **Given** a fruta está à frente, mas há parte do corpo da cobra entre a cabeça e ela, **When**
   o jogador atira, **Then** a língua para no corpo e não come a fruta.
5. **Given** a língua está esticada, **When** a cobra continua andando, **Then** a partida não para:
   a cobra segue no seu ritmo e a língua acompanha a cabeça até voltar.

---

### User Story 2 - Ícone com recarga em forma de relógio (Priority: P1)

Um ícone da língua fica na tela durante a partida. Enquanto recarrega, ele aparece apagado e uma
área iluminada vai se completando como o ponteiro de um relógio (sem números). Quando a recarga
termina, o ícone dá um pulso com um som de "pronto"; enquanto estiver disponível, continua
pulsando e brilhando de leve, para ser percebido com a visão periférica.

**Why this priority**: sem saber quando a língua está pronta, a habilidade fica imprevisível.

**Independent Test**: usar a língua e observar o ícone apagar, o relógio se completar, o pulso e o
som ao ficar pronto, e o brilho contínuo enquanto disponível.

**Acceptance Scenarios**:

1. **Given** a língua foi usada, **When** a recarga começa, **Then** o ícone fica apagado e uma
   fatia iluminada cresce no sentido horário a partir do topo, proporcional ao tempo já recarregado.
2. **Given** a recarga em andamento, **When** ela termina, **Then** o ícone volta à cor cheia, dá
   um pulso (cresce e volta ao tamanho) e toca um som curto de "pronto".
3. **Given** a língua disponível, **When** o jogador está jogando, **Then** o ícone pulsa e brilha
   de leve continuamente, sem atrapalhar a leitura do tabuleiro.
4. **Given** o jogo em pausa, **When** o jogador olha o ícone, **Then** a recarga está parada e
   continua de onde parou ao retomar.

---

### User Story 3 - Sons da língua (Priority: P2)

Disparar a língua tem um som próprio (um "tchum" elástico); comer pela língua usa o som de coleta.

**Why this priority**: reforça o feedback; a mecânica funciona sem ele.

**Independent Test**: atirar a língua com e sem fruta ao alcance e ouvir os sons.

**Acceptance Scenarios**:

1. **Given** a língua disponível, **When** o jogador atira, **Then** toca o som do disparo.
2. **Given** a língua alcança a fruta, **When** a fruta é comida, **Then** toca o som de coleta
   (e o "pop" do placar), como numa coleta normal.
3. **Given** a língua em recarga, **When** o jogador aperta o botão, **Then** nenhum som toca.

---

### Edge Cases

- Fruta exatamente no limite do alcance: é alcançada; uma casa além: não.
- Fruta na casa imediatamente à frente da cabeça: a língua a come (equivale a comer um passo antes).
- Comer pela língua leva o placar a um limiar do Feeding Frenzy: o Frenzy começa normalmente, e a
  língua fica bloqueada durante ele (FR-005).
- A recarga termina durante o Frenzy: o pulso e o som de "pronto" acontecem quando o Frenzy acaba
  e o ícone deixa de ficar acinzentado.
- Comer pela língua ocupa a última casa livre: vitória, como numa coleta normal.
- Direção mudada no mesmo passo em que a língua é disparada: a língua sai na direção atual da
  cabeça (a que a cobra está andando naquele momento).
- Colisão enquanto a língua está esticada: fim de jogo normal; a língua some.
- Restart, "Tela inicial" e nova partida: a língua começa disponível.
- Botão apertado fora da partida (menus, contagem, abertura do Frenzy, "SURVIVED!"): ignorado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Durante a partida, a tecla Espaço DEVE disparar a língua na direção em que a cabeça
  está andando, se a língua estiver disponível; nos menus, Espaço continua confirmando.
- **FR-002**: Se houver fruta ao alcance nessa linha, sem parede ou corpo da cobra no caminho, ela
  DEVE ser comida como numa coleta normal (placar, crescimento, efeitos e sons de coleta).
- **FR-003**: O alcance da língua DEVE ser de 3 casas à frente da cabeça.
- **FR-004**: Disparar a língua, acertando ou não, DEVE iniciar uma recarga de 8 s; durante a
  recarga o botão não tem efeito.
- **FR-005**: Durante o Feeding Frenzy (da abertura até "SURVIVED!" ou o fim de jogo), a língua
  DEVE ficar bloqueada: o botão não tem efeito nem som, e o ícone aparece acinzentado, sem pulso
  nem brilho. A recarga continua contando normalmente por baixo; ao fim do Frenzy, o ícone volta
  a mostrar o estado real (pronto ou recarregando).
- **FR-006**: A língua DEVE aparecer esticando e voltando (ida e volta em até 0,3 s), sem parar a
  partida; a fruta acertada é puxada junto na volta.
- **FR-007**: Um ícone da língua DEVE ficar visível durante a partida, fixo no canto inferior
  esquerdo da tela, com cerca de duas casas de tamanho (sem cobrir o placar nem o cronômetro do
  Frenzy).
- **FR-008**: Durante a recarga, o ícone DEVE ficar apagado com uma fatia iluminada em forma de
  relógio (sentido horário, a partir do topo) proporcional ao progresso; sem números.
- **FR-009**: Ao fim da recarga, o ícone DEVE dar um pulso e tocar um som de "pronto".
- **FR-010**: Enquanto disponível, o ícone DEVE pulsar e brilhar de leve continuamente.
- **FR-011**: A recarga DEVE parar na pausa (e nas telas em que a partida está parada) e voltar de
  onde parou.
- **FR-012**: Disparar a língua DEVE tocar um som próprio; apertar durante a recarga não toca som.
- **FR-013**: A língua DEVE começar disponível em toda partida nova.
- **FR-014**: A mesma seed e as mesmas entradas DEVEM produzir os mesmos disparos e coletas.

### Key Entities

- **Língua**: estado (disponível, esticando, voltando, em recarga), alcance, direção do disparo e a
  fruta puxada (se acertou).
- **Recarga**: tempo total e tempo já recarregado (progresso de 0 a 1).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Do aperto do botão até a fruta ser comida, no máximo 0,15 s.
- **SC-002**: 100% dos disparos com fruta ao alcance e caminho livre comem a fruta; 0% comem com o
  caminho bloqueado ou fora do alcance.
- **SC-003**: O jogador percebe que a língua ficou pronta sem olhar diretamente para o ícone (pulso
  + som + brilho contínuo).
- **SC-004**: A recarga mostrada no ícone fica a no máximo 0,1 s do tempo real de jogo corrido.
- **SC-005**: O jogo mantém 60 quadros por segundo com a língua e o ícone animando.

## Assumptions

- A fruta é comida no instante do disparo (a regra é decidida na hora); a animação de ida e volta
  é só visual, o que mantém a resposta imediata (SC-001).
- A língua atravessa casas vazias e para na primeira parede ou parte do corpo.
- O som de "pronto" respeita o volume de Efeitos, como os demais.
