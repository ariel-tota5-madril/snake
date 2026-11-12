import ast
from pathlib import Path

import snake.core
import snake.flow
import snake.juice
import snake.menu

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
