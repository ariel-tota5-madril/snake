"""Menus do jogo (tela inicial, pausa, fim de partida, Opções): seleção sem renderização (Princípio I)."""

from enum import Enum


class MenuOption(Enum):
    PLAY = "Jogar"
    RANKING = "Ranking"  # 005/FR-010b
    OPTIONS = "Opções"
    CONTINUE = "Continuar"
    TITLE = "Tela inicial"
    PLAY_AGAIN = "Jogar de novo"  # 005
    QUIT = "Sair"  # 005: fica na tela inicial
    MUSIC = "Música"
    SFX = "Efeitos"
    BACK = "Voltar"


TITLE_OPTIONS = (MenuOption.PLAY, MenuOption.RANKING, MenuOption.OPTIONS, MenuOption.QUIT)  # 005
PAUSE_OPTIONS = (MenuOption.CONTINUE, MenuOption.OPTIONS, MenuOption.TITLE)
END_OPTIONS = (MenuOption.PLAY_AGAIN, MenuOption.TITLE)  # 005/FR-010: opções do placar
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
    """Opções do placar ao fim da partida (005/FR-010): "Jogar de novo" e "Tela inicial"."""

    def __init__(self) -> None:
        super().__init__(END_OPTIONS)


NAME_MAX = 10
NAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ")


class NameEntry:
    """Campo do nome do jogador (005/FR-002): até 10 letras, dígitos ou espaços ASCII."""

    def __init__(self, initial: str = "") -> None:
        self.text = initial[:NAME_MAX]

    def type(self, ch: str) -> bool:
        """Acrescenta um caractere; devolve True se o texto mudou."""
        if len(ch) != 1 or ch not in NAME_CHARS or len(self.text) >= NAME_MAX:
            return False
        self.text += ch
        return True

    def backspace(self) -> bool:
        if not self.text:
            return False
        self.text = self.text[:-1]
        return True

    @property
    def value(self) -> str:
        return self.text.strip()

    @property
    def confirmable(self) -> bool:
        return self.value != ""
