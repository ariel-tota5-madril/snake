from snake.menu import (
    END_OPTIONS,
    PAUSE_OPTIONS,
    SETTINGS_OPTIONS,
    TITLE_OPTIONS,
    EndMenu,
    Menu,
    MenuOption,
)


# T019
def test_option_sets():
    assert TITLE_OPTIONS == (MenuOption.PLAY, MenuOption.OPTIONS)
    assert PAUSE_OPTIONS == (MenuOption.CONTINUE, MenuOption.OPTIONS, MenuOption.TITLE)
    assert END_OPTIONS == (MenuOption.RESTART, MenuOption.OPTIONS, MenuOption.QUIT)
    assert SETTINGS_OPTIONS == (MenuOption.MUSIC, MenuOption.SFX, MenuOption.BACK)


def test_menu_starts_on_first_option():
    assert Menu(PAUSE_OPTIONS).selected is MenuOption.CONTINUE
    assert EndMenu().selected is MenuOption.RESTART
    assert EndMenu().options == END_OPTIONS


def test_moves_report_change_and_stop_at_the_ends():
    menu = Menu(END_OPTIONS)
    assert menu.move_up() is False and menu.selected is MenuOption.RESTART
    assert menu.move_down() is True and menu.selected is MenuOption.OPTIONS
    assert menu.move_down() is True and menu.selected is MenuOption.QUIT
    assert menu.move_down() is False and menu.selected is MenuOption.QUIT
    assert menu.move_up() is True and menu.selected is MenuOption.OPTIONS


def test_confirm_returns_selected_option():
    menu = Menu(TITLE_OPTIONS)
    assert menu.confirm() is MenuOption.PLAY
    menu.move_down()
    assert menu.confirm() is MenuOption.OPTIONS
