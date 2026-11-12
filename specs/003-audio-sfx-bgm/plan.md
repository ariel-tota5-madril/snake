# Implementation Plan: Áudio — efeitos sonoros e música 8-bit

**Branch**: `003-audio-sfx-bgm` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-audio-sfx-bgm/spec.md`

## Summary

Adicionar efeitos sonoros e música 8-bit sintetizados pelo próprio jogo, mais um menu de pausa
(Esc), um menu na tela inicial ("Jogar"/"Opções"), "Opções" no menu de fim de partida e uma tela
de Opções com sliders de volume salvos entre sessões. Abordagem:

- **Síntese pura** (`synth.py`): gera amostras PCM 16-bit a partir de notas com ondas quadrada,
  triangular e ruído, envelopes e mixagem — sem Pygame, sem NumPy, determinística.
- **Catálogo** (`sounds.py`): descreve cada efeito, jingle e música como notas; testável sem
  áudio.
- **Eventos sonoros** (`flow.py`): o `Flow` registra o que deve soar (passo, coleta, pico do
  pulso, batida, contagem, navegação, confirmação, jingles, troca de música) numa fila; ele
  continua sem saber nada de áudio.
- **Configuração** (`settings.py`): volumes com passos de 10%, salvos em JSON.
- **Adaptador de áudio** (`audio.py`): único módulo que fala com `pygame.mixer`; se o mixer não
  abrir, vira um áudio mudo.
- **Telas novas no `Flow`**: pausa, contagem de retomada, Opções; menus generalizados.

## Technical Context

**Language/Version**: Python 3.12 (compatível com 3.12+; `.venv` local em 3.13)

**Primary Dependencies**: Pygame 2.6 (`pygame.mixer` apenas em `audio.py`); biblioteca padrão
(`array`, `math`, `json`, `random`) nos módulos puros — **sem dependências novas**

**Storage**: arquivo JSON com os volumes em `~/.config/snake/settings.json` (caminho injetável)

**Testing**: pytest sobre `synth`, `sounds`, `settings`, `menu` e `flow`, sem abrir janela nem
tocar som

**Target Platform**: desktop com janela gráfica; saída de áudio opcional (FR-013)

**Project Type**: desktop-app (jogo local)

**Performance Goals**: 60 fps com áudio ativo (SC-004); síntese de todos os sons ao abrir o jogo
em menos de 2 s; atraso evento → som ≤ 50 ms (SC-001)

**Constraints**: mixer mono 22 050 Hz, 16 bits, buffer de 512 amostras (~23 ms); som não altera
estado do jogo (FR-014); RNG do ruído próprio e semeado (Princípio III)

**Scale/Scope**: ~14 efeitos, 2 jingles, 2 músicas em loop; 4 módulos novos; `flow.py`, `menu.py`
e `app.py` alterados

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Status |
|-----------|---------------------|--------|
| I. Núcleo puro, casca fina | `core.py` intocado. Síntese, catálogo, configuração, menus e fluxo são puros; só `audio.py` e `app.py` tocam Pygame. O `Flow` só emite eventos sonoros, não toca som | ✅ |
| II. Test-first para regras | Cada regra nova (eventos e seus momentos, teclas ignoradas sem som, pausa, retomada, Opções, volumes, persistência, loop sem estalo) entra por um teste que falha antes | ✅ |
| III. Simulação determinística | Síntese é função pura das notas; o ruído usa gerador próprio com seed fixa; o `Flow` emite os mesmos eventos para as mesmas entradas e `dt`; pausa congela o tempo do jogo | ✅ |
| IV. Sem complexidade prematura | Sem NumPy nem bibliotecas de áudio; síntese mínima (3 formas de onda + envelope linear); notas em listas simples. Ver Complexity Tracking para as fases novas | ✅ (justificado) |
| V. Jogável em todo checkpoint | Cada fase do `tasks.md` termina com `python -m snake` abrindo e `pytest` verde; sem áudio, o jogo segue funcionando | ✅ |

**Re-check pós-design (Phase 1)**: os contratos expõem só tipos próprios (`SoundEvent`,
`AudioSettings`, `Menu`, amostras `array('h')`); `audio.py` é o único consumidor de
`pygame.mixer`. Gate continua aprovado.

## Project Structure

### Documentation (this feature)

```text
specs/003-audio-sfx-bgm/
├── plan.md              # Este arquivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── audio-api.md     # synth, sounds, settings, audio
│   └── flow-api.md      # eventos sonoros, pausa, Opções, menus (delta sobre a 002)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
src/snake/
├── core.py          # inalterado
├── juice.py         # inalterado
├── synth.py         # NOVO: ondas, envelopes, mixagem, notas → array('h') (puro)
├── sounds.py        # NOVO: catálogo de SFX, jingles e músicas como notas (puro)
├── settings.py      # NOVO: AudioSettings (0–100, passo 10) + load/save JSON
├── menu.py          # GENERALIZADO: Menu(options), opções de título/pausa/fim/Opções
├── flow.py          # ALTERADO: SoundEvent + fila; pausa, retomada, Opções; menus novos
├── audio.py         # NOVO: adaptador pygame.mixer (ou mudo) que toca os eventos
└── app.py           # ALTERADO: Esc, ←/→ em Opções, desenho dos menus/sliders, áudio

tests/
├── test_synth.py        # NOVO
├── test_sounds.py       # NOVO
├── test_settings.py     # NOVO
├── test_menu.py         # atualizado (menus generalizados)
├── test_flow.py         # ampliado (eventos sonoros, pausa, Opções)
└── test_core_purity.py  # ampliado (synth, sounds, settings sem pygame/time)
```

**Structure Decision**: mantém o layout das features anteriores. O áudio segue o mesmo padrão
da 002: decisões puras e testáveis (`Flow` emite eventos, `sounds` define os sons) e um
adaptador fino (`audio.py`) que só executa.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 7 fases novas no `Flow` (`PAUSE_IN`, `PAUSE`, `PAUSE_OUT`, `RESUME`, `OPTIONS_IN`, `OPTIONS`, `OPTIONS_OUT`) | A spec exige pausa com animação, contagem de retomada e Opções acessível de três telas com retorno à tela de origem | Uma pilha genérica de telas seria mais abstração do que o necessário para três origens; flags soltas no `app.py` não seriam testáveis |
| Síntese de áudio própria (`synth.py`) | FR-001 exige áudio criado pelo projeto, 8-bit, sem arquivos de terceiros | Arquivos WAV prontos violariam FR-001; NumPy seria uma dependência nova sem necessidade (síntese pura é rápida o bastante: 16 s em ~30 ms) |
