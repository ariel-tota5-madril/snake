"""Menus do jogo (tela inicial, pausa, fim de partida, Opções): seleção sem renderização (Princípio I)."""

from enum import Enum


class MenuOption(Enum):
    PLAY = "Jogar"
    OPTIONS = "Opções"
    CONTINUE = "Continuar"
    TITLE = "Tela inicial"
    RESTART = "Restart"
    QUIT = "Quit"
    MUSIC = "Música"
    SFX = "Efeitos"
    BACK = "Voltar"


TITLE_OPTIONS = (MenuOption.PLAY, MenuOption.OPTIONS)
PAUSE_OPTIONS = (MenuOption.CONTINUE, MenuOption.OPTIONS, MenuOption.TITLE)
END_OPTIONS = (MenuOption.RESTART, MenuOption.OPTIONS, MenuOption.QUIT)
SETTINGS_OPTIONS = (MenuOption.MUSIC, MenuOption.SFX, MenuOption.BACK)


class Menu:
    def __init__(self, options: tuple[MenuOption, ...]) -> None:
        self.options = options
        self._index = 0

    @property
    def selected(self) -> MenuOption:
        return self.options[self._index]

    def move_up(self) -> bool:
        """Sobe uma opção (sem volta circular); devolve True se a seleção mudou."""
        before = self._index
        self._index = max(self._index - 1, 0)
        return self._index != before

    def move_down(self) -> bool:
        before = self._index
        self._index = min(self._index + 1, len(self.options) - 1)
        return self._index != before

    def confirm(self) -> MenuOption:
        return self.selected


class EndMenu(Menu):
    """Menu de fim de partida (001/002), agora com "Opções" (003/FR-016)."""

    def __init__(self) -> None:
        super().__init__(END_OPTIONS)
