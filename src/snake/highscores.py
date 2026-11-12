"""Placar de highscore: as 10 melhores pontuações e persistência em JSON. Lógica pura.

Ordem decrescente de pontos; empate deixa o resultado mais antigo acima (005/FR-006). Cada
partida é uma entrada, então o mesmo nome pode repetir (FR-008). Arquivo ruim -> placar vazio.
"""

import json
from dataclasses import dataclass
from pathlib import Path

CAPACITY = 10
NAME_MAX = 10


@dataclass(frozen=True)
class Entry:
    name: str
    score: int


def _valid(item) -> bool:
    if not isinstance(item, dict):
        return False
    name, score = item.get("name"), item.get("score")
    return (
        isinstance(name, str)
        and 0 < len(name.strip()) <= NAME_MAX
        and isinstance(score, int)
        and not isinstance(score, bool)
        and score >= 0
    )


class Highscores:
    def __init__(self, entries: list[Entry] | None = None) -> None:
        self.entries: list[Entry] = list(entries or [])

    def rank_for(self, score: int) -> int | None:
        """Posição (0 = 1º) que a pontuação ocuparia; None se não entra no placar."""
        rank = sum(1 for e in self.entries if e.score >= score)
        return rank if rank < CAPACITY else None

    def insert(self, name: str, score: int) -> int | None:
        rank = self.rank_for(score)
        if rank is None:
            return None
        self.entries.insert(rank, Entry(name, score))
        del self.entries[CAPACITY:]
        return rank

    @classmethod
    def load(cls, path) -> "Highscores":
        try:
            data = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            return cls()
        if not isinstance(data, list):
            return cls()
        entries = [Entry(item["name"].strip(), item["score"]) for item in data if _valid(item)]
        entries.sort(key=lambda e: -e.score)  # sort estável: empates mantêm a ordem do arquivo
        return cls(entries[:CAPACITY])

    def save(self, path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([{"name": e.name, "score": e.score} for e in self.entries]))
