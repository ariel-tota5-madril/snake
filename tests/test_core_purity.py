import ast
from pathlib import Path

import snake.core

FORBIDDEN = {"pygame", "time", "datetime"}


# T027 — Princípio I e III: o núcleo não importa renderização nem relógio
def test_core_does_not_import_rendering_or_clock():
    tree = ast.parse(Path(snake.core.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & FORBIDDEN, f"núcleo importa {imported & FORBIDDEN}"
