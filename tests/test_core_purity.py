import ast
from pathlib import Path

import snake.core
import snake.flow
import snake.frenzy
import snake.juice
import snake.menu
import snake.settings
import snake.sounds
import snake.synth

FORBIDDEN = {"pygame", "time", "datetime"}


def imports_of(module) -> set[str]:
    tree = ast.parse(Path(module.__file__).read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    return imported


# T027 — Princípio I e III: o núcleo não importa renderização nem relógio
def test_core_does_not_import_rendering_or_clock():
    imported = imports_of(snake.core)
    assert not imported & FORBIDDEN, f"núcleo importa {imported & FORBIDDEN}"


# T033 — o menu também é lógica pura
def test_menu_does_not_import_rendering_or_clock():
    imported = imports_of(snake.menu)
    assert not imported & FORBIDDEN, f"menu importa {imported & FORBIDDEN}"


# 002 / T002 — efeitos e fluxo de telas também são lógica pura
def test_juice_and_flow_do_not_import_rendering_or_clock():
    for module in (snake.juice, snake.flow):
        imported = imports_of(module)
        assert not imported & FORBIDDEN, f"{module.__name__} importa {imported & FORBIDDEN}"


# 003 / T002 — síntese, catálogo e configuração também são lógica pura
def test_audio_logic_modules_do_not_import_rendering_or_clock():
    for module in (snake.synth, snake.sounds, snake.settings):
        imported = imports_of(module)
        assert not imported & FORBIDDEN, f"{module.__name__} importa {imported & FORBIDDEN}"


# 004 / T002 — regras do Feeding Frenzy também são lógica pura
def test_frenzy_does_not_import_rendering_or_clock():
    imported = imports_of(snake.frenzy)
    assert not imported & FORBIDDEN, f"frenzy importa {imported & FORBIDDEN}"
