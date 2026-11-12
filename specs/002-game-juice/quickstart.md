# Quickstart: validar o game juice

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Regras (automático)

```bash
pytest
```

**Esperado**: todos os testes passam, incluindo os da 001 (as regras não mudaram). Os testes
novos cobrem durações e determinismo dos efeitos (`test_juice.py`) e a sequência de telas
(`test_flow.py`). Nenhum teste abre janela.

## 2. Jogo (manual)

```bash
python -m snake
```

| # | Ação | Resultado esperado |
|---|------|--------------------|
| 0 | Abrir o jogo | janela de 1440×1440 com grade 30×30 (casas de 48 px); textos proporcionais |
| 1 | Abrir o jogo | tela "Snake / Pressione Espaço para começar" entra animada sobre o tabuleiro escurecido; a cobra não anda |
| 2 | Pressionar uma seta na tela inicial | nada acontece |
| 3 | Pressionar Espaço | a tela inicial sai animada; aparecem "3", "2", "1" (um por segundo) e o placar entra deslizando; cobra e comida visíveis e parados |
| 4 | Pressionar setas durante a contagem | nada acontece; a cobra começa a andar só depois do "1" |
| 5 | Comer uma fruta | partículas saem da cabeça e somem em menos de 1 s; o placar dá um salto rápido (1,8×), quica e assenta, piscando de branco para amarelo; a tela dá um tremor curto e leve |
| 6 | Comer duas frutas seguidas | as partículas se somam e o pulso reinicia, sem travar |
| 7 | Bater na parede | a tela treme brevemente e para; depois a janela de fim entra animada |
| 8 | No menu, confirmar "Restart" | a janela sai animada e começa a contagem (sem voltar à tela inicial) |
| 9 | No menu, ↓ e Enter | o jogo fecha imediatamente |

Contratos: [contracts/juice-api.md](contracts/juice-api.md),
[contracts/flow-api.md](contracts/flow-api.md); regras de tempo e fases em
[data-model.md](data-model.md).
