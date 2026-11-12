"""Configuração de áudio (volumes) com persistência em JSON. Sem Pygame.

Volumes de 0 a 100 em passos de 10 (FR-017). Arquivo ausente ou inválido -> padrão (FR-019).
"""

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MUSIC = 60
DEFAULT_SFX = 80
STEP = 10
FIELDS = ("music", "sfx")


def _snap(value: int) -> int:
    return max(0, min(100, round(value / STEP) * STEP))


@dataclass
class AudioSettings:
    music: int = DEFAULT_MUSIC
    sfx: int = DEFAULT_SFX

    def adjust(self, field: str, direction: int) -> bool:
        """Soma ±10 ao volume `field` (limitado a 0–100); devolve True se o valor mudou."""
        if field not in FIELDS:
            raise ValueError(f"campo desconhecido: {field}")
        before = getattr(self, field)
        after = _snap(before + STEP * (1 if direction > 0 else -1))
        setattr(self, field, after)
        return after != before

    @classmethod
    def load(cls, path: Path) -> "AudioSettings":
        try:
            data = json.loads(Path(path).read_text())
            values = {}
            for field in FIELDS:
                value = data[field]
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
                    raise ValueError(field)
                values[field] = _snap(value)
            return cls(**values)
        except (OSError, ValueError, KeyError, TypeError):
            return cls()

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"music": self.music, "sfx": self.sfx}))
