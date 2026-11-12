"""Menu de fim de partida: seleção entre "Restart" e "Quit", sem renderização (Princípio I)."""

from enum import Enum


class MenuOption(Enum):
    RESTART = "Restart"
    QUIT = "Quit"


class EndMenu:
    options = (MenuOption.RESTART, MenuOption.QUIT)

    def __init__(self) -> None:
        self._index = 0

    @property
    def selected(self) -> MenuOption:
        return self.options[self._index]

    def move_up(self) -> None:
        self._index = max(self._index - 1, 0)

    def move_down(self) -> None:
        self._index = min(self._index + 1, len(self.options) - 1)

    def confirm(self) -> MenuOption:
        return self.selected
