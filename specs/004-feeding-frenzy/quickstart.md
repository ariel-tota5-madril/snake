# Quickstart: validar o Feeding Frenzy

```bash
cd "Aula 3/snake"
source .venv/bin/activate
pytest            # tudo verde
python -m snake   # jogar
```

## Roteiro manual

| # | Passo | Esperado |
|---|-------|----------|
| 1 | Começar uma partida e comer 5 frutas | a cobra acelera um pouco a cada fruta (FR-001/002) |
| 2 | Chegar a 10 pontos | a cobra para, a música para; "FEEDING" (roxo) e "FRENZY" (amarelo) caem na diagonal, cada uma com boom, detritos e tremor (US3) |
| 3 | Fim da abertura | música tensa e rápida; cronômetro "20" grande no topo, "10 restantes" abaixo; placar some; 10 frutas roxas e douradas pulsando; a cobra anda bem mais rápido (FR-006/012) |
| 4 | Comer frutas especiais | partículas da cor da fruta, som de coleta, contador cai; a cobra não cresce e o placar não muda (FR-007/016) |
| 5 | Esc durante o Frenzy | pausa; o cronômetro para; "Continuar" → retoma de onde parou (US2 cenário 9) |
| 6 | Deixar chegar aos 5 s | cronômetro vermelho, pulsando e com tique a cada segundo (FR-019) |
| 7 | Comer a última especial a tempo | partida para; "SURVIVED!" azul entra suave e sai; música normal volta; fruta normal no tabuleiro; mesmo tamanho de antes; velocidade normal (US4) |
| 8 | Chegar a 20 pontos | novo Frenzy; o próximo só aos 40 (FR-004) |
| 9 | Deixar o tempo acabar num Frenzy | "0" piscando em vermelho, alarme, sem tremor; jingle de derrota e menu de fim (FR-010) |
| 10 | Restart | partida normal, velocidade inicial; Frenzy de novo só aos 10 pontos |
| 11 | Bater na parede durante um Frenzy | fim de jogo como colisão normal (FR-011) |
| 12 | Observar fps durante a abertura e o Frenzy | sem engasgos visíveis (SC-006) |

Dica para chegar rápido aos limiares: o roteiro de testes `test_flow.py` usa um condutor guloso
com seed fixa; para teste manual, basta jogar normalmente — 10 frutas levam ~1 minuto.
