# Snake

Jogo Snake em Python, construído com Spec-Driven Development (GitHub Spec Kit).
Especificações, planos e tarefas por feature em [`specs/`](specs/)
(001: núcleo do jogo; 002: game juice; 003: áudio, pausa e Opções; 004: Feeding Frenzy; 005: highscore; 006: língua de Yoshi);
regras do projeto em [`.specify/memory/constitution.md`](.specify/memory/constitution.md).

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Testes

```bash
pytest
```

## Jogar

```bash
python -m snake
```

Fluxo de telas: **tela inicial** ("Jogar" / "Ranking" / "Opções" / "Sair") → **seu nome** → **contagem
3, 2, 1** → **partida** → ao bater, a tela treme → **placar de highscore** ("Jogar de novo" /
"Tela inicial").

- Setas ou WASD: mudam a direção da cobra; nos menus, ↑/↓ escolhem a opção; em Opções, ←/→
  ajustam o volume; no placar, ↑/↓ rolam e ←/→ escolhem a opção. Na entrada de nome, as letras
  são digitadas (Backspace apaga, Enter confirma, Esc volta).
- Input buffer: até 2 direções apertadas em sequência rápida ficam guardadas e são aplicadas uma
  por passo (ex.: ↓ e ← quase juntos fazem a curva completa em vez de perder o segundo comando).
- Espaço ou Enter: confirmam a opção do menu. Na partida, Espaço dispara a língua (veja abaixo).
- Esc: pausa a partida ("Continuar" / "Opções" / "Tela inicial"); na pausa, continua; em Opções,
  volta. Ao continuar, há uma contagem rápida de 1,5 s.
- "Jogar de novo" volta direto para a contagem, com o mesmo nome; "Sair" (tela inicial) fecha o
  jogo.

## Velocidade e Feeding Frenzy

A cobra acelera conforme cresce: um passo a cada 125 ms com 3 segmentos, 1 ms mais rápido por
segmento, até o limite de 70 ms.

Aos **10, 20, 40, 80…** pontos começa o **Feeding Frenzy**: o jogo para, "FEEDING" e "FRENZY"
são carimbadas na tela e entra uma música tensa. A fruta normal some e aparecem 10 frutas
especiais (roxas e douradas). Você tem **20 s** para comer todas, com a cobra 1,5× mais rápida
(mínimo de 50 ms por passo). No modo, a cobra não cresce e o placar não sobe. Nos últimos 5 s o
cronômetro fica vermelho e faz tique. Comeu todas: "SURVIVED!" e a partida volta ao normal, com o
mesmo tamanho. O tempo acabou: fim de jogo.

## Língua de Yoshi

Na partida, **Espaço** dispara a língua para a frente: se a fruta estiver a até **3 casas**, na
mesma linha e sem parede ou corpo no caminho, ela é comida na hora (conta como uma coleta normal).
Todo disparo, acertando ou não, recarrega por **8 s**. O ícone no canto inferior esquerdo mostra a
recarga como um relógio que se ilumina; ao ficar pronta, pulsa com um som e continua brilhando de
leve. No Feeding Frenzy a língua fica bloqueada (ícone acinzentado).

## Highscore

Ao fim de cada partida aparece o placar com as **10 melhores** pontuações (nome até 10
caracteres), salvo em `~/.config/snake/highscores.json`. Se você entra no placar, seu nome vira um
foguete: sempre decola de baixo da 10ª posição, sobe atropelando quem está no caminho (os nomes
explodem, se remontam uma linha abaixo e ficam vermelhos; num placar cheio, o antigo 10º cai para
fora) e pousa na posição nova — "1ST PLACE!" no 1º lugar. "Ranking", na tela inicial, mostra o
placar só para consulta. Enter pula a animação. Arquivo ausente ou
inválido: o jogo abre com o placar vazio.

## Áudio

Efeitos e músicas 8-bit são **sintetizados pelo próprio jogo** ao abrir (sem arquivos de som).
Os volumes de Música e Efeitos (0–100%) ficam salvos em `~/.config/snake/settings.json`; se o
arquivo faltar ou estiver inválido, o jogo usa 60% / 80%. Sem dispositivo de áudio, o jogo
funciona normalmente, em silêncio.

## Estrutura

- `src/snake/core.py` — núcleo puro: todas as regras, sem Pygame, sem relógio, RNG injetado.
- `src/snake/highscores.py` — placar das 10 melhores e persistência em JSON (sem Pygame).
- `src/snake/scoreboard.py` — animação do placar: foguete, câmera, explosões, rolagem (sem Pygame).
- `src/snake/tongue.py` — recarga e animação da língua de Yoshi (sem Pygame).
- `src/snake/frenzy.py` — curva de velocidade, limiares e cronômetro do Feeding Frenzy (sem Pygame).
- `src/snake/menu.py` — menus (tela inicial, pausa, fim, Opções) sem Pygame.
- `src/snake/synth.py` — síntese 8-bit: ondas, rampas e mixagem (sem Pygame).
- `src/snake/sounds.py` — catálogo de efeitos, jingles e músicas compostas em notas (sem Pygame).
- `src/snake/settings.py` — volumes e persistência em JSON (sem Pygame).
- `src/snake/audio.py` — adaptador `pygame.mixer` (ou mudo, se não houver áudio).
- `src/snake/juice.py` — efeitos: partículas, pulso do placar, tremor (sem Pygame nem relógio).
- `src/snake/flow.py` — fases de tela, relógio de passos e eventos sonoros; recebe o tempo de fora
  (sem Pygame).
- `src/snake/app.py` — adaptador Pygame: teclado e relógio → `Flow`, desenho.
- `tests/` — testes das regras e das telas, todos sem abrir janela.
