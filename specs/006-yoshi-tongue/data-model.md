# Data Model: Língua de Yoshi

## `core.py` (delta)

| Nome | Definição |
|------|-----------|
| `TongueShot(direction, reach, ate, target)` | resultado do disparo: direção usada, casas alcançadas (0–3), se comeu e a casa da fruta comida (ou `None`) |
| `Game.tongue(reach=3) -> TongueShot` | regra do disparo (research.md §1); só age com `status == RUNNING` |
| `Game._grow: int` | crescimentos pendentes: no próximo passo a cauda não anda |

### Ordem do `step()` (delta)

Passo 5 passa a ser: move a cabeça; se não comeu fruta normal **e** não há crescimento pendente, a
cauda anda; se havia crescimento pendente, ele é consumido. Com crescimento pendente, a cauda
conta como corpo na colisão.

## `tongue.py` (novo)

| Nome | Definição |
|------|-----------|
| `COOLDOWN_MS = 8000`, `REACH = 3`, `ANIM_MS = 300` | regras |
| `Tongue.remaining_ms` | 0 = pronta |
| `Tongue.ready`, `Tongue.progress` | `remaining == 0`; `1 − remaining / 8000` |
| `Tongue.fire(shot)` | recarga cheia; guarda `shot`; inicia a animação |
| `Tongue.update_cooldown(dt) -> bool` | `True` no instante em que fica pronta |
| `Tongue.update_anim(dt)` | avança a animação |
| `Tongue.extension -> float` | 0 → 1 → 0 durante a animação; 0 fora dela |
| `Tongue.shot -> TongueShot \| None` | último disparo (para o desenho) |

## Flow (delta)

| Campo / método | Regra |
|----------------|-------|
| `tongue: Tongue` | nova a cada partida |
| `tongue_locked: bool` | `game.in_frenzy` |
| `icon_pulse: ScorePulse` | pulso do ícone ao ficar pronto |
| `space()` | `PLAYING`: dispara; demais fases: `confirm()` |

### Eventos sonoros novos

| Momento | Evento |
|---------|--------|
| disparo | `TONGUE` (+ `EAT` e `PULSE_POP` se comeu) |
| fica pronta (fora do Frenzy) ou o Frenzy acaba com ela pronta | `TONGUE_READY` |
