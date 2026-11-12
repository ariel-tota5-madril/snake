# Quickstart: validar áudio, pausa e Opções

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Regras (automático)

```bash
pytest
```

**Esperado**: todos os testes passam, incluindo os das features 001 e 002. Os testes novos
cobrem a síntese (duração, limites, emenda do loop), o catálogo de sons, os volumes e a
persistência, os eventos sonoros e as telas de pausa e Opções. Nenhum teste abre janela nem toca
som.

## 2. Jogo (manual, com som ligado)

```bash
python -m snake
```

| # | Ação | Resultado esperado |
|---|------|--------------------|
| 1 | Abrir o jogo | música animada da tela inicial; menu "Jogar" / "Opções" |
| 2 | ↓ e ↑ no menu | bipe a cada mudança; nas pontas, sem som |
| 3 | "Opções" → ←/→ em Música e Efeitos | barra muda de 10 em 10%; música muda na hora; Efeitos toca uma amostra |
| 4 | "Voltar" e fechar/reabrir o jogo | volumes mantidos |
| 5 | "Jogar" | som de confirmação; bipes em 3, 2, 1 e um "vai!" mais agudo; música de partida começa |
| 6 | Jogar um pouco | tique suave a cada passo, discreto mesmo após 2 minutos |
| 7 | Comer uma fruta | som de coleta e, logo depois, um "pop" no salto do placar |
| 8 | Esc | jogo congela, menu de pausa, música mais baixa |
| 9 | "Continuar" | contagem rápida 3, 2, 1 (1,5 s) e a cobra segue do mesmo ponto e direção |
| 10 | Esc → "Tela inicial" | partida abandonada; volta a música e o menu da tela inicial |
| 11 | Bater na parede | som de batida com o tremor; música para; jingle de derrota com o menu |
| 12 | Menu de fim → "Opções" → "Voltar" | volta ao menu de fim |
| 13 | Rodar com `SDL_AUDIODRIVER=dummy python -m snake` (sem áudio) | jogo funciona normalmente, em silêncio |

Contratos: [contracts/audio-api.md](contracts/audio-api.md),
[contracts/flow-api.md](contracts/flow-api.md); eventos e fases em [data-model.md](data-model.md).
