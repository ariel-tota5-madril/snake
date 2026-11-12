# Data Model: Núcleo do Snake

Coordenadas são pares `(x, y)` de inteiros: `x` cresce para a direita, `y` cresce para baixo,
origem `(0, 0)` no canto superior esquerdo.

## Direction

Enumeração: `UP (0, -1)`, `DOWN (0, 1)`, `LEFT (-1, 0)`, `RIGHT (1, 0)`.

- Oposta de uma direção: o vetor negado (ex.: oposta de `RIGHT` é `LEFT`).

## Status

Enumeração: `RUNNING`, `GAME_OVER`, `WON`.

## Game (estado da partida)

| Campo | Tipo | Regra |
|-------|------|-------|
| `width`, `height` | int | padrão 20 × 20; fixos durante a partida (FR-001) |
| `snake` | lista de casas, cabeça primeiro | começa com 3 casas no centro, apontando para a direita: `[(10,10), (9,10), (8,10)]` na grade 20 × 20 (FR-002) |
| `direction` | Direction | começa em `RIGHT` |
| `pending` | Direction ou nenhum | no máximo um comando por passo (FR-005) |
| `food` | casa ou nenhum | sempre uma casa livre enquanto `RUNNING` (FR-006); nenhum quando não há casa livre |
| `score` | int | começa em 0; +1 por comida (FR-009) |
| `status` | Status | começa em `RUNNING` |
| `rng` | `random.Random` | injetado; única fonte de aleatoriedade (FR-008) |

### Validações

- Todas as casas da cobra e a comida ficam dentro de `0 ≤ x < width` e `0 ≤ y < height`.
- A comida nunca coincide com uma casa da cobra.
- As casas da cobra são todas distintas.

## Transições de estado

```text
RUNNING ──step(): cabeça sairia da grade──────────────► GAME_OVER
RUNNING ──step(): cabeça entraria no corpo─────────────► GAME_OVER
RUNNING ──step(): comeu e não há casa livre p/ comida──► WON
RUNNING ──step(): demais casos─────────────────────────► RUNNING
GAME_OVER / WON ──step() ou turn()─────────────────────► sem mudança (FR-013)
```

## Passo de jogo (`step`), em ordem

1. Se `status` não é `RUNNING`, não faz nada.
2. Aplica `pending` (se houver) a `direction` e limpa `pending`.
3. Calcula a nova cabeça = cabeça + vetor da direção.
4. Se a nova cabeça está fora da grade → `GAME_OVER`.
5. `vai_comer` = nova cabeça == `food`.
6. Corpo considerado = cobra inteira se `vai_comer`, senão cobra sem a cauda. Se a nova cabeça
   está no corpo considerado → `GAME_OVER`.
7. Insere a nova cabeça; se não `vai_comer`, remove a cauda.
8. Se `vai_comer`: `score += 1` e gera nova comida; sem casa livre → `food` nenhum e `WON`.
