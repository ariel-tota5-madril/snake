# Contract: API pública do núcleo (`snake.core`)

Esta é a única interface que o adaptador Pygame e os testes usam. Nenhum tipo do Pygame aparece
aqui (Princípio I).

## Tipos

- `Direction` — enum com `UP`, `DOWN`, `LEFT`, `RIGHT`.
- `Status` — enum com `RUNNING`, `GAME_OVER`, `WON`.
- `Cell` — `tuple[int, int]` no formato `(x, y)`.

## `Game`

### Construção

```text
Game(width: int = 20, height: int = 20, rng: random.Random | None = None, seed: int | None = None)
```

- Cria a partida no estado inicial descrito em `data-model.md` e já posiciona a primeira comida.
- Se `rng` for informado, ele é usado; senão, cria `random.Random(seed)`.

### Comandos

| Método | Efeito |
|--------|--------|
| `turn(direction: Direction) -> None` | registra a direção para o próximo passo; ignora a oposta à atual e qualquer comando depois do primeiro válido no mesmo passo; sem efeito fora de `RUNNING` |
| `step() -> None` | avança um passo, seguindo a ordem de `data-model.md` |

### Consultas (somente leitura)

| Atributo | Tipo | Significado |
|----------|------|-------------|
| `width`, `height` | int | tamanho da grade |
| `snake` | `tuple[Cell, ...]` | casas da cobra, cabeça primeiro |
| `direction` | Direction | direção atual |
| `food` | `Cell | None` | casa da comida (`None` só após vitória) |
| `score` | int | pontuação atual |
| `status` | Status | situação da partida |

## Garantias

- Mesma seed + mesma sequência de `turn`/`step` → mesma sequência de estados (FR-008, SC-004).
- Enquanto `status == RUNNING`: exatamente uma comida, fora da cobra (FR-006, SC-002).
- `score` == número de comidas comidas (FR-009, SC-003).
- Fora de `RUNNING`, `turn` e `step` não alteram nenhum atributo (FR-013).
