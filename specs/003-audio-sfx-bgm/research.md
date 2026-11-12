# Research: Áudio 8-bit, pausa e Opções

## 1. Origem do áudio

- **Decision**: sintetizar tudo em tempo de execução, ao abrir o jogo, a partir de notas
  descritas no código (`sounds.py`), com `synth.py` gerando PCM mono 16-bit a 22 050 Hz.
- **Rationale**: FR-001 (criado pelo projeto, sem terceiros, estilo 8-bit); nada de arquivos
  binários no repositório; medido: 16 s de onda em ~30 ms em Python puro.
- **Alternatives considered**: WAVs gerados por script e versionados (artefatos binários sem
  necessidade); NumPy (dependência nova; a síntese pura já é rápida — Princípio IV).

## 2. Formas de onda (estilo 8-bit)

- **Decision**: quadrada com duty de 50%, 25% e 12,5% (melodia e efeitos), triangular (baixo) e
  ruído por registrador de deslocamento (LFSR de 15 bits, como consoles clássicos) para batida e
  percussão. Envelope linear de ataque/decaimento; frequência pode deslizar (efeitos que sobem ou
  descem).
- **Rationale**: são os timbres característicos de 8-bit; LFSR é determinístico (Princípio III).

## 3. Loop sem estalo (SC-003)

- **Decision**: cada nota começa e termina com rampa de 2 ms; a música tem duração exata de um
  número inteiro de compassos; o loop é feito pelo próprio mixer (`play(loops=-1)`).
- **Rationale**: amostra final e inicial perto de zero não geram estalo na emenda.

## 4. Músicas

- **Decision**: duas faixas originais, em lá menor/dó maior, 3 vozes (melodia quadrada, baixo
  triangular, percussão de ruído):
  - **Tela inicial**: 120 BPM, 8 compassos, clima animado e convidativo.
  - **Partida**: 150 BPM, 8 compassos, mais energética.
  - **Jingles**: derrota (4 notas descendentes, ~1,2 s) e vitória (arpejo ascendente, ~1,5 s).
- **Rationale**: "upbeat" pedido pelo usuário; loops curtos bastam para um jogo casual.

## 5. Efeitos e volumes relativos

| Evento | Som | Volume relativo |
|--------|-----|-----------------|
| passo | tique triangular curto (20 ms), grave | 0,15 (o menor, FR-002) |
| coleta | quadrada 25%, sobe uma oitava em 80 ms | 0,7 |
| pico do pulso | "pop" quadrada 12,5%, 40 ms, agudo | 0,5 |
| batida | ruído descendente, 350 ms | 0,9 |
| contagem 3/2/1 | bipe quadrado 80 ms | 0,6 |
| "vai!" | bipe uma quinta acima, 250 ms | 0,7 |
| navegação | blip 30 ms | 0,4 |
| confirmação | dois blips ascendentes, 120 ms | 0,6 |
| amostra de volume | igual à coleta | 0,7 |

Volume tocado = volume relativo × slider (Efeitos ou Música). A música também é multiplicada por
0,5 (fica abaixo dos efeitos, FR-011) e por 0,35 extra durante a pausa (FR-015).

## 6. Eventos sonoros saem do `Flow`

- **Decision**: o `Flow` acrescenta `SoundEvent`s numa fila durante `update`/entradas; o
  adaptador chama `flow.drain_sounds()` a cada quadro e toca. O pico do pulso é um evento
  agendado 60 ms após a coleta.
- **Rationale**: o `Flow` já é onde os momentos acontecem; a fila mantém o `Flow` sem áudio
  (Princípio I) e torna "qual som, quando" testável (Princípio II). Teclas ignoradas não geram
  evento (FR-010) porque o `Flow` só emite quando a ação acontece.

## 7. Mixer e falta de áudio

- **Decision**: `pygame.mixer.pre_init(22050, -16, 1, 512)` e 16 canais; música num canal
  reservado; se `pygame.mixer.init()` falhar, `audio.py` usa um objeto mudo com a mesma interface.
- **Rationale**: buffer de 512 amostras ≈ 23 ms (SC-001 ≤ 50 ms); FR-013.

## 8. Persistência dos volumes

- **Decision**: JSON `{"music": 60, "sfx": 80}` em `~/.config/snake/settings.json`, salvo ao sair
  de Opções; leitura tolerante: arquivo ausente, JSON inválido, tipos errados ou valores fora de
  0–100 → padrão 60/80. Valores lidos são arredondados para múltiplos de 10.
- **Rationale**: FR-019 e caso de borda de arquivo inválido; caminho injetável para teste.

## 9. Pausa, retomada e Opções no `Flow`

- **Decision**: novas fases `PAUSE_IN` → `PAUSE` → `PAUSE_OUT` → `RESUME` (1,5 s, números a
  cada 0,5 s) → `PLAYING`; "Tela inicial" vai de `PAUSE_OUT` para `TITLE_IN` e recomeça a partida.
  `OPTIONS_IN` → `OPTIONS` → `OPTIONS_OUT` voltam à fase de origem (`TITLE`, `PAUSE` ou `MENU`).
  Durante a pausa, o tempo do jogo e dos efeitos não avança.
- **Rationale**: reaproveita o padrão de fases com entrada/saída animada da 002.

## 10. Menus

- **Decision**: `menu.py` passa a ter um `Menu(options)` genérico e opções nomeadas: título
  (`PLAY`, `OPTIONS`), pausa (`CONTINUE`, `OPTIONS`, `TITLE`), fim (`RESTART`, `OPTIONS`, `QUIT`)
  e Opções (`MUSIC`, `SFX`, `BACK`). `move_up`/`move_down` informam se a seleção mudou (para o
  bipe de navegação só tocar quando muda).
- **Rationale**: FR-009, FR-016, FR-017; um menu genérico evita quatro classes parecidas.
