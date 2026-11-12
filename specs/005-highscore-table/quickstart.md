# Quickstart: validar o Highscore

```bash
cd "Aula 3/snake"
source .venv/bin/activate
pytest
python -m snake
```

Para começar com o placar vazio: `rm ~/.config/snake/highscores.json`.

| # | Passo | Esperado |
|---|-------|----------|
| 1 | Abrir o jogo | tela inicial com Jogar / Opções / Sair |
| 2 | Jogar | entrada de nome; digitar "ANA", Backspace apaga, Enter com campo vazio não faz nada |
| 3 | Enter com nome | contagem 3, 2, 1 e partida |
| 4 | Perder (placar vazio) | jingle; placar vertical; "ANA" com chama, tremor e pouso no 1º; "1ST PLACE!"; opções |
| 5 | ←/→ e A/D | troca entre "Jogar de novo" e "Tela inicial" |
| 6 | Jogar de novo | contagem direto, sem pedir nome |
| 7 | Fazer 5+ partidas | placar com mais de 5 linhas; ↑/↓ e W/S rolam; setas ▲/▼ indicam mais conteúdo |
| 8 | Bater várias posições | foguete sobe na tela, câmera segue (lista desce), cada nome explode e se remonta abaixo; ao ver o 1º, o foguete termina a subida na tela |
| 9 | Placar cheio (10) e entrar nele | o antigo 10º explode e cai na ignição |
| 10 | Pontuação que não entra | placar sem animação; resultado abaixo dele |
| 11 | Enter durante a animação | pula para o fim |
| 12 | Tela inicial → Jogar | nome já preenchido com o último |
| 13 | Fechar e abrir | placar mantido |
| 14 | WASD na partida e nos menus | funciona como setas |
| 15 | Sair na tela inicial | fecha o jogo |
| 16 | Corromper o JSON e abrir | abre com placar vazio, sem erro |
