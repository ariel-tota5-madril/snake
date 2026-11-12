# Contract: módulos de áudio

## `snake.synth` (puro)

| Função | Contrato |
|--------|----------|
| `render(notes: list[Note]) -> array('h')` | concatena as notas em sequência; cada nota com rampa de 2 ms no início e no fim |
| `mix(*tracks: array('h')) -> array('h')` | soma faixas (a mais curta é completada com silêncio) e limita a [−32767, 32767] |
| `Note(wave, freq, ms, volume=1.0, freq_end=None)` | `wave` ∈ `square50`, `square25`, `square12`, `triangle`, `noise`; `freq == 0` é pausa |

Garantias: mesma entrada → mesmas amostras (o ruído usa LFSR com estado inicial fixo); nenhuma
amostra fora de [−32767, 32767]; duração = soma das durações (± 1 amostra por nota).

## `snake.sounds` (puro)

| Membro | Contrato |
|--------|----------|
| `SFX: dict[SoundEvent, tuple[array('h'), float]]` | amostras e volume relativo de cada efeito (`STEP`, `EAT`, `PULSE_POP`, `CRASH`, `COUNT`, `GO`, `NAV`, `CONFIRM`, `VOLUME_PREVIEW`) |
| `JINGLES: dict[SoundEvent, array('h')]` | `LOSE`, `WIN` |
| `MUSIC: dict[SoundEvent, array('h')]` | `MUSIC_TITLE`, `MUSIC_GAME` (loops de compassos inteiros) |
| `build()` | gera todos os sons (chamado uma vez ao abrir o jogo) |

Garantia: `STEP` tem o menor volume relativo de todos os efeitos (FR-002).

## `snake.settings` (puro + arquivo)

| Membro | Contrato |
|--------|----------|
| `AudioSettings(music=60, sfx=80)` | inteiros 0–100 em passos de 10 |
| `adjust(field: str, direction: int) -> bool` | `field` ∈ `"music"`, `"sfx"`; ±10 limitado; `True` se mudou |
| `AudioSettings.load(path) -> AudioSettings` | qualquer falha ou valor inválido → padrão 60/80 |
| `save(path)` | grava JSON e cria a pasta se preciso |

## `snake.audio` (adaptador Pygame)

| Membro | Contrato |
|--------|----------|
| `Audio.create(settings) -> Audio` | inicia o mixer; se falhar, devolve `SilentAudio` com a mesma interface |
| `play(event: SoundEvent)` | toca efeito/jingle, ou troca/para/abaixa a música, conforme o evento |
| `apply_volumes(settings)` | atualiza volumes imediatamente (FR-018) |

Volume tocado: efeito = relativo × `sfx/100`; música = `MUSIC_GAIN` × `music/100` (× `PAUSE_DUCK`
durante a pausa).
