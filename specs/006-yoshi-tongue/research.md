# Research: Língua de Yoshi

## 1. Alcance e coleta no núcleo

- **Decision**: `Game.tongue(reach=3) -> TongueShot(direction, reach, ate)`. Percorre as casas
  `cabeça + d × direção` para `d = 1..3`: parede ou corpo param a língua (alcance `d − 1`, sem
  coleta); a fruta normal em `d` é comida (alcance `d`). A direção é a atual da cabeça
  (`game.direction`), não a curva ainda guardada no buffer de entradas.
- **Coleta**: placar +1, nova fruta sorteada pelo RNG do jogo (vitória se não houver casa livre) e
  `_grow += 1`: no próximo passo a cauda não anda — a cobra cresce como se tivesse comido.
- **Rationale**: SC-001 (coleta no mesmo quadro), FR-002 (igual a uma coleta normal), FR-014
  (decidido pelo estado, sem tempo).
- **Alternatives considered**: comer quando a animação chega na fruta (adiaria a coleta ~150 ms e
  dependeria de tempo dentro do núcleo).

## 2. Recarga

- **Decision**: `Tongue(cooldown_ms=8000)`: `fire(shot)` zera a recarga (`remaining_ms = 8000`) e
  inicia a animação; `update_cooldown(dt)` desconta e devolve `True` no instante em que fica pronta;
  `progress = 1 − remaining/8000`; `ready = remaining == 0`. A animação (`update_anim(dt)`, 300 ms:
  150 ida + 150 volta) é separada para poder continuar mesmo quando a recarga está parada.
- O `Flow` só chama `update_cooldown` em `PLAYING` (a recarga para na pausa, contagem, abertura do
  Frenzy, "SURVIVED!", tempo esgotado — FR-011) e continua contando durante o Frenzy (FR-005).
- A animação anda junto com os demais efeitos (congela só na pausa).

## 3. Bloqueio no Frenzy e aviso de "pronto"

- **Decision**: `tongue_locked = game.in_frenzy` (vale da abertura até o fim do modo). Bloqueada,
  `space()` não faz nada nem toca som; o ícone é desenhado acinzentado.
- **Aviso**: o `Flow` guarda `_ready_announced`. Quando a língua está pronta, não está bloqueada e o
  aviso ainda não foi dado, emite `TONGUE_READY` e dispara o pulso do ícone. Se ficou pronta durante
  o Frenzy, o aviso sai quando o modo termina e a partida volta a andar.
- Partida nova: língua pronta, aviso já considerado dado (sem som no começo).

## 4. Espaço

- **Decision**: `Flow.space()`: em `PLAYING` dispara a língua; em qualquer outra fase equivale a
  `confirm()`. Enter continua só confirmando. Na entrada de nome, Espaço é texto (o adaptador já
  manda letras e espaço como texto).

## 5. Sons

| Evento | Som | Volume relativo |
|--------|-----|-----------------|
| `TONGUE` | quadrada 25% descendo 900 → 300 Hz, 120 ms, + ruído curto | 0,6 |
| `TONGUE_READY` | dois bipes ascendentes (1 320 → 1 760 Hz), 160 ms | 0,55 |

Comer pela língua reaproveita `EAT` e o `PULSE_POP` agendado (FR-002).

## 6. Desenho

- **Língua**: retângulo rosa com ponta arredondada saindo da cabeça na direção do disparo; o
  comprimento é `reach × extensão(t)` (0 → 1 em 150 ms, 1 → 0 em 150 ms). Se comeu, uma "fruta
  fantasma" é desenhada na ponta durante a volta.
- **Ícone** (≈ 2 casas, canto inferior esquerdo, 16 px de margem): círculo com uma língua estilizada.
  - Recarregando: versão escura + fatia clara em forma de relógio (polígono do centro até o arco, de
    −90° no sentido horário, proporcional ao `progress`).
  - Pronto: cor cheia; pulso de escala (`ScorePulse`) ao ficar pronto; halo com brilho senoidal de
    ~1,2 s.
  - Bloqueado (Frenzy): tons de cinza, sem pulso nem halo.
