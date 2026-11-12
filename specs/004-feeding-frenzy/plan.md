# Implementation Plan: Feeding Frenzy — velocidade progressiva e modo de sobrevivência

**Branch**: `004-feeding-frenzy` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-feeding-frenzy/spec.md`

## Summary

Duas regras novas de jogo e um modo especial com encenação própria:

- **Velocidade progressiva**: o intervalo entre passos deixa de ser fixo (125 ms) e passa a ser
  `max(70, 125 − (tamanho − 3))` ms; no Frenzy, `max(50, normal / 1,5)`.
- **Feeding Frenzy**: aos 10, 20, 40, 80… pontos, a fruta normal some e surgem 10 frutas
  especiais (alternando roxa/dourada); 20 s para comer todas, sem crescer nem pontuar. Sucesso →
  "SURVIVED!" e volta ao normal; tempo esgotado → alarme e fim de jogo.
- **Encenação**: abertura com "FEEDING"/"FRENZY" carimbadas (boom, detritos, tremor), música
  própria tensa a 180 BPM, cronômetro com aviso nos últimos 5 s, "SURVIVED!" com entrada suave.

Abordagem técnica (mesmo padrão das features anteriores):

- **Regras puras**: `core.py` ganha frutas especiais (`start_frenzy`/`end_frenzy`/`fail`);
  `frenzy.py` (novo) concentra limiares, curva de velocidade e cronômetro — tudo testável sem
  Pygame e sem relógio.
- **Fluxo** (`flow.py`): três fases novas (`FRENZY_INTRO`, `SURVIVED`, `TIMEOUT`), passo com
  intervalo variável e novos eventos sonoros.
- **Efeitos** (`juice.py`): `ease_in` para o carimbo e `ParticleBurst` parametrizável (quantidade,
  velocidade, vida, tom) para os detritos do impacto e as partículas coloridas.
- **Som** (`sounds.py`): boom, tique do cronômetro, alarme e a música do Frenzy, sintetizados
  como os demais; `audio.py` não muda.
- **Desenho** (`app.py`): carimbos girados, cronômetro, contador, frutas especiais pulsantes e
  "SURVIVED!".

## Technical Context

**Language/Version**: Python 3.12 (compatível com 3.12+; `.venv` local em 3.13)

**Primary Dependencies**: Pygame 2.6 (só em `app.py` e `audio.py`); biblioteca padrão nos
módulos puros — **sem dependências novas**

**Storage**: N/A (nada novo é persistido)

**Testing**: pytest sobre `core`, `frenzy`, `juice`, `sounds` e `flow`, sem janela nem som

**Target Platform**: desktop com janela gráfica (1440×1440, grade 30×30)

**Project Type**: desktop-app (jogo local)

**Performance Goals**: 60 fps com o Frenzy ativo (SC-006): 10 frutas pulsantes, cronômetro e
até ~100 partículas de detritos simultâneas; síntese da música nova somada às atuais ainda em
menos de 2 s na abertura do jogo

**Constraints**: cronômetro com erro ≤ 0,1 s em relação ao tempo de jogo corrido (SC-004);
abertura ≤ 2,5 s e "SURVIVED!" ≤ 2 s (SC-005); mesma seed + mesmas entradas → mesmas frutas
especiais e mesmo desfecho (SC-007)

**Scale/Scope**: 1 módulo novo (`frenzy.py`); `core.py`, `juice.py`, `flow.py`, `sounds.py` e
`app.py` alterados; 4 eventos sonoros novos (`BOOM`, `TIMER_TICK`, `TIMEOUT_ALARM`,
`MUSIC_FRENZY`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | Frutas especiais e falha por tempo vivem no `core.py`; limiares, curva de velocidade e cronômetro em `frenzy.py` (puro); o `Flow` só orquestra e emite eventos; Pygame continua restrito a `app.py`/`audio.py` | ✅ |
| II. Test-first para regras | Curva de velocidade, sequência de limiares, sorteio e consumo das frutas especiais, cronômetro (incluindo empate tempo × última fruta), fases novas e eventos sonoros entram por testes que falham antes | ✅ |
| III. Simulação determinística | Frutas especiais sorteadas pelo RNG do jogo sobre a lista ordenada de casas livres; cronômetro avança só por `dt` injetado; detritos usam o RNG de efeitos já existente | ✅ |
| IV. Sem complexidade prematura | Sem engine de animação nem pilha de cenas: três fases com tempos fixos, no mesmo padrão das anteriores. Ver Complexity Tracking | ✅ (justificado) |
| V. Jogável em todo checkpoint | Velocidade progressiva (US1) é entregável sozinha; o Frenzy funciona sem a encenação (US2) antes de ganhar abertura (US3) e "SURVIVED!" (US4) | ✅ |

**Re-check pós-design (Phase 1)**: os contratos expõem só tipos próprios (`Game`, `Frenzy`,
`Phase`, `SoundEvent`, `ParticleBurst`); `audio.py` não muda e continua o único consumidor de
`pygame.mixer`. Gate continua aprovado.

## Project Structure

### Documentation (this feature)

```text
specs/004-feeding-frenzy/
├── plan.md              # Este arquivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── core-frenzy-api.md   # core (frutas especiais) + frenzy (limiares, velocidade, cronômetro)
│   └── flow-api.md          # fases, consultas e eventos sonoros novos (delta sobre a 003)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
src/snake/
├── core.py          # ALTERADO: specials, start_frenzy(), end_frenzy(), fail(); restart limpa
├── frenzy.py        # NOVO: threshold(n), step_interval_ms(), Frenzy (cronômetro, aviso)
├── juice.py         # ALTERADO: ease_in; ParticleBurst(count, speed, life, tint)
├── flow.py          # ALTERADO: passo variável; FRENZY_INTRO / SURVIVED / TIMEOUT; eventos novos
├── sounds.py        # ALTERADO: BOOM, TIMER_TICK, TIMEOUT_ALARM, música do Frenzy
├── audio.py         # inalterado (toca o que estiver nos catálogos)
└── app.py           # ALTERADO: carimbos, cronômetro, contador, frutas especiais, SURVIVED!

tests/
├── test_speed.py        # NOVO: curva de velocidade (normal e Frenzy)
├── test_frenzy.py       # NOVO: limiares, cronômetro, aviso dos 5 s; regras do core no Frenzy
├── test_juice.py        # ampliado (ease_in, ParticleBurst parametrizado)
├── test_sounds.py       # ampliado (sons e música novos)
├── test_flow.py         # ampliado (entrada/saída do Frenzy, fases, eventos) e ajustado
│                        #   para o passo variável
└── test_core_purity.py  # ampliado (frenzy.py sem pygame/time)
```

**Structure Decision**: mantém o layout das features anteriores. O Frenzy é uma regra de jogo
(o que acontece ao comer, quando se perde), então o estado das frutas fica no `core`; o tempo
real é coisa do `Flow`, que recebe `dt` de fora, e por isso o cronômetro vive em `frenzy.py`
e é avançado pelo `Flow`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 3 fases novas no `Flow` (`FRENZY_INTRO`, `SURVIVED`, `TIMEOUT`) | A spec exige a partida parada durante a abertura, durante "SURVIVED!" e no aviso de tempo esgotado, cada uma com tempo e eventos próprios | Flags dentro de `PLAYING` misturariam "a cobra anda" com "a cobra está parada" e quebrariam a regra atual de que Esc só pausa em `PLAYING` |
| Módulo novo `frenzy.py` | Limiares, curva de velocidade e cronômetro são regras puras com testes próprios | Colocar no `flow.py` (já com ~360 linhas) misturaria regra com orquestração de telas; colocar no `core.py` traria tempo real para o núcleo, que é por passos |
