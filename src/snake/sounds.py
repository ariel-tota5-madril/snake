"""Catálogo de efeitos, jingles e músicas 8-bit, descritos como notas. Lógica pura.

Todo o áudio é composto aqui e sintetizado por `snake.synth` (FR-001: criado pelo projeto).
"""

from array import array

from snake.flow import SoundEvent
from snake.synth import Note, mix, render

SFX: dict[SoundEvent, tuple[array, float]] = {}
JINGLES: dict[SoundEvent, array] = {}
MUSIC: dict[SoundEvent, array] = {}


def _gameplay_sfx() -> None:
    # (amostras, volume relativo) — volumes de research.md §5; o passo é o mais baixo (FR-002)
    SFX[SoundEvent.STEP] = (render([Note("triangle", 220, 20, decay=1)]), 0.15)
    SFX[SoundEvent.EAT] = (render([Note("square25", 523, 80, freq_end=1046)]), 0.7)
    SFX[SoundEvent.PULSE_POP] = (render([Note("square12", 1568, 40, decay=1)]), 0.5)
    SFX[SoundEvent.CRASH] = (render([Note("noise", 6000, 350, freq_end=700, decay=1)]), 0.9)


# --- notação musical -------------------------------------------------------------------

NOTE_INDEX = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def freq(name: str) -> float:
    """'A4' -> 440 Hz; aceita sustenido ('F#4'); 'R' é pausa."""
    if name == "R":
        return 0.0
    letter, sharp, octave = name[0], name.count("#"), int(name[-1])
    semitones = NOTE_INDEX[letter] + sharp + 12 * (octave - 4)
    return 440.0 * 2 ** (semitones / 12)


def voice(wave: str, bpm: int, notes: list[tuple[str, float]], volume: float, decay: float = 0.0):
    beat_ms = 60000 / bpm
    return render([Note(wave, freq(n), beats * beat_ms, volume, decay=decay) for n, beats in notes])


def bass_line(chords: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Baixo em colcheias alternando fundamental e oitava (ex.: ('A2', 4) = 4 tempos de A)."""
    line = []
    for root, beats in chords:
        octave = root[:-1] + str(int(root[-1]) + 1)
        line += [(root, 0.5), (octave, 0.5)] * int(beats)
    return line


def drum_track(bpm: int, bars: int, volume: float) -> array:
    """Bumbo nos tempos 1 e 3, caixa no 2 e 4, chimbal nas colcheias."""
    eighth = 60000 / bpm / 2
    kick = Note("noise", 1200, eighth, volume, freq_end=300, decay=1)
    hat = Note("noise", 16000, eighth, volume * 0.35, decay=1)
    snare = Note("noise", 9000, eighth, volume * 0.8, decay=1)
    bar = [kick, hat, snare, hat, kick, hat, snare, hat]
    return render(bar * bars)


def song(bpm: int, melody, chords, lead: str, bars: int) -> array:
    return mix(
        voice(lead, bpm, melody, 0.42),
        voice("triangle", bpm, bass_line(chords), 0.55),
        drum_track(bpm, bars, 0.22),
    )


# --- músicas (composições originais) ---------------------------------------------------

TITLE_BPM = 120
TITLE_MELODY = [
    ("C5", .5), ("E5", .5), ("G5", .5), ("E5", .5), ("A5", 1), ("G5", 1),
    ("F5", .5), ("E5", .5), ("D5", .5), ("C5", .5), ("D5", 1), ("G4", 1),
    ("C5", .5), ("E5", .5), ("G5", .5), ("C6", .5), ("B5", 1), ("G5", 1),
    ("A5", .5), ("G5", .5), ("F5", .5), ("D5", .5), ("C5", 2),
    ("E5", .5), ("G5", .5), ("A5", .5), ("G5", .5), ("E5", 1), ("C5", 1),
    ("D5", .5), ("E5", .5), ("F5", .5), ("A5", .5), ("G5", 2),
    ("E5", .5), ("F5", .5), ("G5", .5), ("C6", .5), ("A5", 1), ("F5", 1),
    ("G5", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("C5", 2),
]
TITLE_CHORDS = [("C2", 4), ("G2", 4), ("C2", 4), ("F2", 2), ("G2", 2),
                ("A2", 4), ("F2", 4), ("F2", 2), ("G2", 2), ("C2", 4)]

GAME_BPM = 150
GAME_MELODY = [
    ("A4", .5), ("C5", .5), ("E5", .5), ("A5", .5), ("G5", .5), ("E5", .5), ("C5", .5), ("E5", .5),
    ("F5", .5), ("E5", .5), ("D5", .5), ("C5", .5), ("D5", 1), ("E5", 1),
    ("A4", .5), ("C5", .5), ("E5", .5), ("A5", .5), ("B5", .5), ("A5", .5), ("G5", .5), ("E5", .5),
    ("F5", .5), ("G5", .5), ("A5", .5), ("G5", .5), ("E5", 2),
    ("C6", .5), ("B5", .5), ("A5", .5), ("G5", .5), ("F5", .5), ("G5", .5), ("A5", .5), ("C6", .5),
    ("B5", .5), ("A5", .5), ("G5", .5), ("E5", .5), ("G5", 2),
    ("A5", .5), ("G5", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("E5", .5), ("F5", .5), ("G5", .5),
    ("E5", 1), ("C5", 1), ("A4", 2),
]
GAME_CHORDS = [("A2", 4), ("F2", 4), ("A2", 4), ("G2", 4), ("C2", 4), ("G2", 4), ("F2", 4), ("E2", 4)]


FRENZY_BPM = 180
_FRENZY_A = ["A4", "C5", "E5", "A5", "E5", "C5", "A4", "C5", "E5", "G5", "E5", "C5", "B4", "C5", "E5", "C5"]
_FRENZY_F = ["F4", "A4", "C5", "F5", "C5", "A4", "F4", "A4", "C5", "E5", "C5", "A4", "G4", "A4", "C5", "A4"]
_FRENZY_G = ["G4", "B4", "D5", "G5", "D5", "B4", "G4", "B4", "D5", "F5", "D5", "B4", "A4", "B4", "D5", "B4"]
_FRENZY_E = ["E4", "G#4", "B4", "E5", "B4", "G#4", "E4", "G#4", "B4", "D5", "B4", "G#4", "F#4", "G#4", "B4", "E5"]
_FRENZY_END = ["E4", "G#4", "B4", "E5", "B4", "G#4", "B4", "D5"]
FRENZY_MELODY = (
    [(n, .25) for n in _FRENZY_A + _FRENZY_F + _FRENZY_G + _FRENZY_E + _FRENZY_A + _FRENZY_F + _FRENZY_G]
    + [(n, .25) for n in _FRENZY_END] + [("E5", 2)]
)  # semicolcheias em lá menor: tensa e rápida (004, research.md §9)
FRENZY_CHORDS = [("A2", 4), ("F2", 4), ("G2", 4), ("E2", 4)] * 2


def _music() -> None:
    MUSIC[SoundEvent.MUSIC_TITLE] = song(TITLE_BPM, TITLE_MELODY, TITLE_CHORDS, "square25", 8)
    MUSIC[SoundEvent.MUSIC_GAME] = song(GAME_BPM, GAME_MELODY, GAME_CHORDS, "square50", 8)
    MUSIC[SoundEvent.MUSIC_FRENZY] = song(FRENZY_BPM, FRENZY_MELODY, FRENZY_CHORDS, "square50", 8)


def _jingles() -> None:
    bpm = 160
    JINGLES[SoundEvent.LOSE] = mix(
        voice("square50", bpm, [("G4", .75), ("E4", .75), ("C4", .75), ("G3", 1)], 0.6, decay=0.6),
        voice("triangle", bpm, [("C3", 2.25), ("C2", 1)], 0.6),
    )
    JINGLES[SoundEvent.WIN] = mix(
        voice("square25", bpm, [("C5", .5), ("E5", .5), ("G5", .5), ("C6", .5), ("E6", 2)], 0.55),
        voice("square50", bpm, [("R", 2), ("G5", 2)], 0.35),
        voice("triangle", bpm, [("C3", 2), ("C2", 2)], 0.6),
    )


def _ui_sfx() -> None:
    SFX[SoundEvent.COUNT] = (render([Note("square50", 880, 80, decay=0.5)]), 0.6)
    SFX[SoundEvent.GO] = (render([Note("square50", 1319, 250, decay=0.6)]), 0.7)  # uma quinta acima
    SFX[SoundEvent.NAV] = (render([Note("square25", 1200, 30, decay=1)]), 0.4)
    SFX[SoundEvent.CONFIRM] = (render([Note("square25", 880, 60), Note("square25", 1319, 60, decay=1)]), 0.6)
    SFX[SoundEvent.VOLUME_PREVIEW] = (SFX[SoundEvent.EAT][0], 0.7)  # amostra = som de coleta
    SFX[SoundEvent.NAME_TYPE] = (render([Note("square25", 1500, 25, decay=1)]), 0.35)  # 005


def _frenzy_sfx() -> None:
    SFX[SoundEvent.TIMER_TICK] = (render([Note("square12", 1760, 35, decay=1)]), 0.5)
    alarm = [Note("square50", f, 100) for f in (880, 660) * 3]
    SFX[SoundEvent.TIMEOUT_ALARM] = (render(alarm), 0.8)
    boom = mix(
        render([Note("noise", 4000, 600, 0.7, freq_end=200, decay=1)]),
        render([Note("triangle", 110, 600, 0.9, freq_end=40, decay=1)]),
    )
    SFX[SoundEvent.BOOM] = (boom, 1.0)  # carimbo "FEEDING"/"FRENZY": o som mais forte do jogo


def _scoreboard_sfx() -> None:
    """005: ignição, decolagem, impacto, pouso e fanfarra do 1º lugar."""
    SFX[SoundEvent.ROCKET_IGNITE] = (render([Note("noise", 600, 700, 0.8, freq_end=2500)]), 0.6)
    SFX[SoundEvent.ROCKET_LAUNCH] = (
        mix(
            render([Note("noise", 3000, 400, 0.6, freq_end=9000, decay=1)]),
            render([Note("square12", 300, 400, 0.5, freq_end=1200, decay=0.8)]),
        ),
        0.8,
    )
    SFX[SoundEvent.ROCKET_HIT] = (
        mix(
            render([Note("noise", 5000, 120, 0.8, freq_end=800, decay=1)]),
            render([Note("square50", 200, 60, 0.5, decay=1)]),
        ),
        0.7,
    )
    SFX[SoundEvent.ROCKET_LAND] = (render([Note("triangle", 200, 200, freq_end=80, decay=1)]), 0.8)
    bpm = 150
    JINGLES[SoundEvent.FIRST_PLACE] = mix(
        voice("square25", bpm, [("C5", .5), ("E5", .5), ("G5", .5), ("C6", 2)], 0.55),
        voice("square50", bpm, [("R", 1.5), ("E5", .5), ("G5", 1.5)], 0.35),
        voice("triangle", bpm, [("C3", 1.5), ("G2", .5), ("C3", 1.5)], 0.6),
    )


def build() -> None:
    """Gera todos os sons (uma vez, ao abrir o jogo)."""
    _gameplay_sfx()
    _ui_sfx()
    _frenzy_sfx()
    _scoreboard_sfx()
    _music()
    _jingles()
