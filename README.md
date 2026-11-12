# Snake

Jogo Snake em Python, construído com Spec-Driven Development (GitHub Spec Kit).
Especificações, planos e tarefas por feature em [`specs/`](specs/)
(001: núcleo do jogo; 002: game juice; 003: áudio, pausa e Opções; 004: Feeding Frenzy);
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

Fluxo de telas: **tela inicial** ("Jogar" / "Opções") → **contagem 3, 2, 1** → **partida** →
ao bater, a tela treme → **menu de fim** ("Restart" / "Opções" / "Quit").

- Setas: mudam a direção da cobra; nos menus, ↑/↓ escolhem a opção; em Opções, ←/→ ajustam o
  volume.
- Espaço ou Enter: confirmam a opção do menu.
- Esc: pausa a partida ("Continuar" / "Opções" / "Tela inicial"); na pausa, continua; em Opções,
  volta. Ao continuar, há uma contagem rápida de 1,5 s.
- "Restart" volta direto para a contagem; "Quit" fecha o jogo.

## Velocidade e Feeding Frenzy

A cobra acelera conforme cresce: um passo a cada 125 ms com 3 segmentos, 1 ms mais rápido por
segmento, até o limite de 70 ms.

Aos **10, 20, 40, 80…** pontos começa o **Feeding Frenzy**: o jogo para, "FEEDING" e "FRENZY"
são carimbadas na tela e entra uma música tensa. A fruta normal some e aparecem 10 frutas
especiais (roxas e douradas). Você tem **20 s** para comer todas, com a cobra 1,5× mais rápida
(mínimo de 50 ms por passo). No modo, a cobra não cresce e o placar não sobe. Nos últimos 5 s o
cronômetro fica vermelho e faz tique. Comeu todas: "SURVIVED!" e a partida volta ao normal, com o
mesmo tamanho. O tempo acabou: fim de jogo.

## Áudio

Efeitos e músicas 8-bit são **sintetizados pelo próprio jogo** ao abrir (sem arquivos de som).
Os volumes de Música e Efeitos (0–100%) ficam salvos em `~/.config/snake/settings.json`; se o
arquivo faltar ou estiver inválido, o jogo usa 60% / 80%. Sem dispositivo de áudio, o jogo
funciona normalmente, em silêncio.

## Estrutura

- `src/snake/core.py` — núcleo puro: todas as regras, sem Pygame, sem relógio, RNG injetado.
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
