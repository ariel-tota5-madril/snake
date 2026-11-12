# Quickstart: validar o núcleo do Snake

## Pré-requisitos

- Python 3.12 ou superior (o `.venv` do projeto usa 3.13).
- Ambiente gráfico para abrir a janela do Pygame.

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Regras (automático)

```bash
pytest
```

**Esperado**: todos os testes passam. Os testes cobrem movimento e direção (US1), comida,
crescimento e determinismo (US2), pontuação (US3), game over, vitória e estado congelado
(FR-011 a FR-013), reinício e menu de fim de partida (FR-014 a FR-016). Nenhum teste abre
janela.

## 2. Jogo (manual)

```bash
python -m snake
```

Roteiro de verificação:

| # | Ação | Resultado esperado |
|---|------|--------------------|
| 1 | Abrir o jogo e não tocar em nada | cobra de 3 casas anda para a direita; pontuação 0; uma comida na grade |
| 2 | Pressionar ↑ e depois ← | a cobra vira para cima e depois para a esquerda |
| 3 | Indo para a direita, pressionar ← | nada muda (direção oposta é ignorada) |
| 4 | Levar a cabeça até a comida | a cobra cresce 1 casa, a pontuação sobe 1, outra comida aparece fora da cobra |
| 5 | Bater na parede | a partida termina e a pontuação final aparece; a cobra para de andar |
| 6 | Em outra partida, bater no próprio corpo | a partida termina e a pontuação final aparece |
| 7 | No fim da partida | aparece o menu com "Restart" (selecionado) e "Quit" |
| 8 | No menu, pressionar Espaço ou Enter | nova partida: cobra de 3 casas no centro, pontuação 0 |
| 9 | No fim de outra partida, pressionar ↓ e Enter | o jogo fecha |
| 10 | Durante a partida, pressionar Espaço ou Enter | nada acontece |

Contratos e regras detalhadas: [contracts/core-api.md](contracts/core-api.md) e
[data-model.md](data-model.md).
