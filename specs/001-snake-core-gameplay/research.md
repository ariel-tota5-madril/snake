# Research: Núcleo do Snake

Não havia itens NEEDS CLARIFICATION no Technical Context. As decisões abaixo registram as
escolhas técnicas e suas alternativas.

## 1. Biblioteca de interface

- **Decision**: Pygame 2.6, usado só em `app.py`.
- **Rationale**: pedido explícito do usuário; tem janela, teclado e relógio prontos; roda em
  Python 3.12 e 3.13.
- **Alternatives considered**: `curses` (terminal; descartado por não ser o pedido);
  `pygame-ce` (fork compatível, sem necessidade de trocar agora).

## 2. Avanço do jogo (tempo)

- **Decision**: o núcleo expõe `step()`; o adaptador chama `step()` em intervalo fixo
  (8 passos/s) usando o relógio do Pygame.
- **Rationale**: Princípio III — o núcleo não conhece tempo real, então testes avançam o jogo
  chamando `step()` diretamente.
- **Alternatives considered**: núcleo com `update(dt)` em segundos (introduz tempo no núcleo e
  quebra a reprodutibilidade).

## 3. Aleatoriedade da comida

- **Decision**: `Game` recebe um `random.Random`; a comida é `rng.choice` sobre a lista
  **ordenada** de casas livres.
- **Rationale**: ordenar as casas livres torna o resultado independente da ordem interna de
  conjuntos, garantindo a mesma sequência de comidas para a mesma seed (FR-008, SC-004).
- **Alternatives considered**: sortear casas até achar uma livre (número de sorteios variável e
  lento com a grade quase cheia).

## 4. Mudança de direção por passo

- **Decision**: `turn()` guarda no máximo uma direção pendente por passo; o **primeiro**
  comando válido do passo vence e os seguintes são ignorados; comandos opostos à direção atual
  são ignorados. `step()` aplica a pendente e a limpa.
- **Rationale**: cumpre FR-004 e FR-005 e impede a inversão rápida (ex.: cima + esquerda dentro
  do mesmo passo indo para a direita).
- **Alternatives considered**: fila de comandos (mais responsiva, mas é complexidade que a spec
  não pede — Princípio IV).

## 5. Colisão com a cauda

- **Decision**: ao checar colisão com o corpo, a casa atual da cauda conta como livre, exceto
  no passo em que a cobra cresce.
- **Rationale**: a cauda sai no mesmo passo em que a cabeça entra (Edge Case da spec).

## 6. Reinício da partida

- **Decision**: `Game.restart()` no núcleo recoloca a partida no estado inicial (FR-002),
  zera a pontuação e gera nova comida **com o mesmo `random.Random`**.
- **Rationale**: reiniciar é regra de jogo, então fica no núcleo (Princípio I); reusar o RNG
  mantém a sessão inteira reproduzível a partir de uma seed (Princípio III).
- **Alternatives considered**: o adaptador criar um `Game()` novo (perde a reprodutibilidade
  entre partidas e espalha a regra de estado inicial pelo adaptador).

## 7. Menu de fim de partida

- **Decision**: módulo puro `menu.py` com `MenuOption` (`RESTART`, `QUIT`) e `EndMenu`
  (`selected`, `move_up()`, `move_down()`, `confirm()`); começa em `RESTART` e não dá a volta
  nas pontas. O adaptador só mostra o menu quando `status` não é `RUNNING` e só então repassa
  ↑/↓/Espaço/Enter para ele.
- **Rationale**: a seleção tem regras próprias da spec (opção inicial, limites, confirmação), e
  testá-las sem janela exige que fiquem fora do Pygame. Duas opções e um índice bastam
  (Princípio IV).
- **Alternatives considered**: tratar a seleção direto no `app.py` (não testável sem janela);
  framework de cenas/telas (complexidade prematura).

## 8. Ambiente Python

- **Decision**: código compatível com Python 3.12+; o `.venv` existente (3.13) é usado sem
  recriar.
- **Rationale**: o usuário pediu 3.12; não há recurso exclusivo de 3.13 no plano, então o mesmo
  código roda nos dois.
