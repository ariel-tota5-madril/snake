# Snake Constitution

## Core Principles

### I. Núcleo Puro, Casca Fina (NÃO NEGOCIÁVEL)

Todas as regras do jogo — grade, cobra, comida, colisão, pontuação e velocidade — DEVEM viver
em um módulo de núcleo livre de renderização.

- O núcleo NÃO PODE importar a biblioteca de renderização/entrada, nem ler o relógio, o teclado
  ou a tela.
- O núcleo DEVE ser testável sem abrir janela nem inicializar interface gráfica.
- Renderização e entrada são um adaptador fino: traduzem eventos em comandos para o núcleo e
  desenham o estado que o núcleo expõe. O adaptador NÃO PODE conter regra de jogo.

**Rationale**: separar regra de apresentação mantém as regras verificáveis por teste e permite
trocar a interface sem tocar na lógica.

### II. Test-First para Regras

Toda criação ou mudança de regra de jogo DEVE começar com um teste `pytest` que falha.

- Ciclo obrigatório: escrever o teste → vê-lo falhar → implementar o mínimo para passar →
  refatorar com a suíte verde.
- Uma mudança de regra sem teste novo ou alterado que a cubra NÃO PODE ser aceita.
- Testes NÃO PODEM ser editados para passar sem que a regra correspondente na spec tenha mudado.

**Rationale**: o teste que falha primeiro prova que a regra está realmente sendo verificada e
documenta o comportamento esperado.

### III. Simulação Determinística

Toda aleatoriedade do núcleo (por exemplo, a posição da comida) DEVE vir de um gerador de números
aleatórios injetado e semeável.

- O núcleo NÃO PODE usar o RNG global nem depender do tempo real para decidir regras.
- O avanço do jogo é feito por passos discretos (ticks) chamados de fora do núcleo.
- Dada a mesma seed, o mesmo estado inicial e a mesma sequência de comandos, o núcleo DEVE
  produzir exatamente a mesma sequência de estados.

**Rationale**: reprodutibilidade torna bugs repetíveis e testes estáveis.

### IV. Sem Complexidade Prematura

Implementar apenas o que a spec atual exige.

- Abstrações, camadas, padrões ou configurações sem uso atual NÃO PODEM ser adicionados.
- Dependências externas só entram quando uma necessidade concreta da spec as justifica.
- Toda complexidade adicional DEVE ser justificada no `plan.md` da feature.

**Rationale**: código mínimo é mais fácil de testar, revisar e mudar quando a spec evoluir.

### V. Jogável em Todo Checkpoint

Cada fatia de implementação DEVE terminar em um estado executável.

- Ao fim de cada fase do `tasks.md`, o jogo DEVE iniciar sem erro e a suíte de testes DEVE passar.
- Funcionalidade incompleta fica fora do fluxo de jogo (não exposta) em vez de quebrá-lo.

**Rationale**: checkpoints jogáveis dão feedback real cedo e evitam integração em massa no fim.

## Restrições de Arquitetura e Testes

- Testes de regra exercitam apenas o núcleo; NÃO PODEM depender da biblioteca de renderização.
- O adaptador de interface é verificado por execução manual do jogo em cada checkpoint
  (Princípio V), não por testes de regra.
- Toda dependência do projeto DEVE estar declarada em um único arquivo de dependências.

## Fluxo de Desenvolvimento

- Todo trabalho segue o fluxo do Spec Kit: spec → clarify (quando houver ambiguidade) → plan →
  tasks → implement.
- Mudanças de comportamento começam pela spec (abordagem spec-anchored): atualizar `spec.md`,
  regenerar `plan.md` e `tasks.md`, depois o código.
- Cada capacidade nova ou correção pós-entrega recebe sua própria pasta numerada em `specs/` e
  sua própria branch.
- Antes de dar uma fase por concluída: suíte `pytest` verde e jogo iniciando sem erro.

## Governance

- Esta constituição prevalece sobre qualquer outra prática, spec, plano ou tarefa do projeto. Em
  caso de conflito, o artefato conflitante DEVE ser corrigido.
- Emendas são feitas via `/speckit-constitution`, com a mudança e sua justificativa registradas
  no Sync Impact Report e versionadas em commit próprio.
- Versionamento semântico: MAJOR para remoção ou redefinição incompatível de princípio; MINOR
  para princípio ou seção nova ou orientação ampliada; PATCH para esclarecimentos e correções de
  texto.
- Todo `plan.md` DEVE passar pelo Constitution Check, e toda revisão de código DEVE verificar a
  conformidade com os Princípios I a V.

**Version**: 1.0.0 | **Ratified**: 2026-11-12 | **Last Amended**: 2026-11-12
