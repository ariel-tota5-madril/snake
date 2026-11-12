# Implementation Plan: Língua de Yoshi — habilidade com cooldown

**Branch**: `006-yoshi-tongue` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-yoshi-tongue/spec.md`

## Summary

Espaço, durante a partida, dispara a língua na direção da cabeça: alcance de 3 casas, parando na
parede ou no corpo; se a fruta estiver no caminho, é comida na hora como uma coleta normal. Todo
disparo inicia uma recarga de 8 s. Um ícone fixo no canto inferior esquerdo mostra a recarga como
um relógio que se ilumina (sem números), pulsa com som ao ficar pronto e brilha de leve enquanto
disponível. No Feeding Frenzy a língua fica bloqueada e o ícone, acinzentado.

Abordagem técnica (padrão das features anteriores):

- **Regra no núcleo** (`core.py`): `Game.tongue(reach)` decide até onde a língua vai e se come a
  fruta; a coleta pela língua faz o crescimento acontecer no próximo passo (a cauda não anda).
- **`tongue.py`** (novo, puro): recarga de 8 s, estado pronto/recarregando, progresso 0–1 e a
  animação visual de ida e volta (300 ms).
- **`flow.py`**: `space()` (língua na partida, confirmação nos menus), bloqueio no Frenzy, aviso
  de "pronto" (adiado se a recarga acabar durante o Frenzy), eventos sonoros `TONGUE` e
  `TONGUE_READY`, efeitos de coleta reaproveitados.
- **`sounds.py`**: "tchum" elástico e o "pronto".
- **`app.py`**: Espaço → `flow.space()`; desenho da língua (esticando e voltando, puxando a fruta)
  e do ícone (relógio, pulso, brilho, acinzentado).

## Technical Context

**Language/Version**: Python 3.12 (compatível com 3.12+; `.venv` local em 3.13)

**Primary Dependencies**: Pygame 2.6 (só em `app.py`/`audio.py`); biblioteca padrão nos módulos
puros — **sem dependências novas**

**Storage**: N/A

**Testing**: pytest sobre `core`, `tongue`, `sounds` e `flow`

**Target Platform**: desktop (janela 1440×1440)

**Project Type**: desktop-app (jogo local)

**Performance Goals**: coleta no mesmo quadro do aperto (SC-001 ≤ 0,15 s); 60 fps (SC-005)

**Constraints**: recarga com erro ≤ 0,1 s em relação ao tempo de jogo corrido (SC-004); mesma
seed + mesmas entradas → mesmos disparos e coletas (FR-014)

**Scale/Scope**: 1 módulo novo (`tongue.py`); `core.py`, `flow.py`, `sounds.py`, `app.py`
alterados; 2 eventos sonoros novos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | Alcance, bloqueio e coleta no `core.py`; recarga em `tongue.py`; o `Flow` orquestra; `app.py` só lê estado e desenha | ✅ |
| II. Test-first para regras | Alcance (exato/fora), bloqueio por corpo/parede, coleta com crescimento no passo seguinte, recarga, erro gastando recarga, bloqueio no Frenzy, aviso adiado, pausa e restart entram por testes que falham antes | ✅ |
| III. Simulação determinística | A coleta é decidida na hora do disparo pelo estado do jogo; recarga só por `dt` injetado; nova fruta pelo RNG do jogo | ✅ |
| IV. Sem complexidade prematura | Um módulo pequeno para a recarga; a animação é só um relógio de 300 ms lido pelo desenho | ✅ |
| V. Jogável em todo checkpoint | US1 (disparo + recarga) jogável antes do ícone (US2) e dos sons (US3) | ✅ |

**Re-check pós-design (Phase 1)**: contratos expõem só tipos próprios (`TongueShot`, `Tongue`);
Pygame continua restrito a `app.py`/`audio.py`. Aprovado.

## Project Structure

### Documentation (this feature)

```text
specs/006-yoshi-tongue/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tongue-api.md     # core (Game.tongue), tongue.py e delta do Flow
└── tasks.md
```

### Source Code (repository root)

```text
src/snake/
├── core.py      # ALTERADO: Game.tongue(reach) -> TongueShot; crescimento pendente
├── tongue.py    # NOVO: Tongue (recarga 8 s, progresso, animação de 300 ms)
├── flow.py      # ALTERADO: space(), bloqueio no Frenzy, aviso de pronto, eventos
├── sounds.py    # ALTERADO: TONGUE, TONGUE_READY
└── app.py       # ALTERADO: Espaço, desenho da língua e do ícone

tests/
├── test_tongue.py       # NOVO: regra do núcleo + recarga
├── test_flow.py         # ampliado
├── test_sounds.py       # ampliado
└── test_core_purity.py  # ampliado (tongue.py)
```

**Structure Decision**: a regra de "o que a língua alcança e come" é regra de jogo e vai para o
núcleo (como a fruta normal); o tempo de recarga é tempo real e fica num módulo puro avançado pelo
`Flow`, como o cronômetro do Frenzy.

## Complexity Tracking

Sem violações a justificar: nenhuma fase nova no `Flow` e um único módulo pequeno.
