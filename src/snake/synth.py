"""Síntese de áudio 8-bit: notas -> amostras PCM 16-bit. Lógica pura, sem Pygame.

Formas de onda clássicas de console (quadrada com 3 duties, triangular e ruído LFSR), rampa de
2 ms no início e no fim de cada nota (sem estalos) e mixagem com limite em 16 bits.
"""

from array import array
from dataclasses import dataclass

SAMPLE_RATE = 22050
RAMP_MS = 2
LIMIT = 32767
AMPLITUDE = 26000  # folga para somar vozes sem estourar tanto
NOISE_CLOCK_HZ = 8000  # taxa do ruído quando freq == 0
DUTY = {"square50": 0.5, "square25": 0.25, "square12": 0.125}
WAVES = set(DUTY) | {"triangle", "noise"}


@dataclass(frozen=True)
class Note:
    wave: str
    freq: float  # Hz; 0 = pausa (exceto no ruído, que usa NOISE_CLOCK_HZ)
    ms: float
    volume: float = 1.0
    freq_end: float | None = None  # se definido, a frequência desliza até este valor
    decay: float = 0.0  # 0 = volume constante; 1 = cai linearmente até 0 no fim da nota

    def __post_init__(self) -> None:
        if self.wave not in WAVES:
            raise ValueError(f"onda desconhecida: {self.wave}")


def _note_samples(note: Note) -> list[int]:
    count = round(SAMPLE_RATE * note.ms / 1000)
    if count <= 0:
        return []
    if note.freq == 0 and note.wave != "noise":
        return [0] * count

    ramp = max(1, round(SAMPLE_RATE * RAMP_MS / 1000))
    start = note.freq or NOISE_CLOCK_HZ
    end = note.freq_end if note.freq_end is not None else start
    peak = AMPLITUDE * note.volume
    phase = 0.0
    lfsr = 1  # estado fixo: o ruído é determinístico
    noise_bit = 1.0
    out = []
    for i in range(count):
        t = i / count
        freq = start + (end - start) * t
        phase += freq / SAMPLE_RATE
        if note.wave == "noise":
            while phase >= 1.0:  # um passo do registrador por ciclo
                phase -= 1.0
                bit = (lfsr ^ (lfsr >> 1)) & 1
                lfsr = (lfsr >> 1) | (bit << 14)
                noise_bit = 1.0 if lfsr & 1 else -1.0
            value = noise_bit
        else:
            phase %= 1.0
            if note.wave == "triangle":
                value = 4 * abs(phase - 0.5) - 1
            else:
                value = 1.0 if phase < DUTY[note.wave] else -1.0
        gain = peak * (1 - note.decay * t)
        if i < ramp:
            gain *= i / ramp
        elif i >= count - ramp:
            gain *= (count - 1 - i) / ramp
        out.append(int(value * gain))
    return out


def render(notes: list[Note]) -> array:
    """Concatena as notas em sequência e devolve amostras 16-bit."""
    out = array("h")
    for note in notes:
        out.extend(_note_samples(note))
    return out


def mix(*tracks: array) -> array:
    """Soma faixas (as mais curtas são completadas com silêncio) e limita a 16 bits."""
    length = max((len(t) for t in tracks), default=0)
    out = array("h", [0] * length)
    for i in range(length):
        total = 0
        for track in tracks:
            if i < len(track):
                total += track[i]
        out[i] = max(-LIMIT, min(LIMIT, total))
    return out
