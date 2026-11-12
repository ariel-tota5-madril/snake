# Quickstart: validar a língua de Yoshi

```bash
cd "Aula 3/snake"
source .venv/bin/activate
pytest
python -m snake
```

| # | Passo | Esperado |
|---|-------|----------|
| 1 | Começar a partida | ícone da língua no canto inferior esquerdo, pronto, pulsando e brilhando de leve |
| 2 | Alinhar a cobra com a fruta a 1–3 casas e apertar Espaço | "tchum", a língua estica e volta puxando a fruta; placar +1, a cobra cresce, efeitos de coleta |
| 3 | Logo depois, apertar Espaço de novo | nada acontece; o ícone está escuro e o relógio vai se iluminando |
| 4 | Esperar 8 s | o relógio fecha, o ícone pulsa e toca o som de "pronto"; volta a brilhar |
| 5 | Atirar com a fruta a 4+ casas | a língua estica 3 casas e volta vazia; recarga começa |
| 6 | Atirar com o corpo entre a cabeça e a fruta | a língua para no corpo; não come |
| 7 | Esc durante a recarga | o relógio para; ao continuar, segue de onde parou |
| 8 | Entrar no Feeding Frenzy | ícone acinzentado; Espaço não faz nada; ao sobreviver, o ícone volta (com pulso e som se ficou pronto durante o Frenzy) |
| 9 | Restart | língua pronta de novo |
| 10 | Menus | Espaço continua confirmando; na entrada de nome, digita espaço |
