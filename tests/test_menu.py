from snake.menu import (
    END_OPTIONS,
    PAUSE_OPTIONS,
    SETTINGS_OPTIONS,
    TITLE_OPTIONS,
    EndMenu,
    Menu,
    MenuOption,
    NameEntry,
)


# T019
def test_option_sets():
    assert TITLE_OPTIONS == (MenuOption.PLAY, MenuOption.RANKING, MenuOption.OPTIONS, MenuOption.QUIT)  # 005
    assert MenuOption.QUIT.value == "Sair"
    assert PAUSE_OPTIONS == (MenuOption.CONTINUE, MenuOption.OPTIONS, MenuOption.TITLE)
    assert END_OPTIONS == (MenuOption.PLAY_AGAIN, MenuOption.TITLE)  # 005/FR-010
    assert MenuOption.PLAY_AGAIN.value == "Jogar de novo"
    assert SETTINGS_OPTIONS == (MenuOption.MUSIC, MenuOption.SFX, MenuOption.BACK)


def test_menu_starts_on_first_option():
    assert Menu(PAUSE_OPTIONS).selected is MenuOption.CONTINUE
    assert EndMenu().selected is MenuOption.PLAY_AGAIN
    assert EndMenu().options == END_OPTIONS


def test_moves_report_change_and_stop_at_the_ends():
    menu = Menu(PAUSE_OPTIONS)
    assert menu.move_up() is False and menu.selected is MenuOption.CONTINUE
    assert menu.move_down() is True and menu.selected is MenuOption.OPTIONS
    assert menu.move_down() is True and menu.selected is MenuOption.TITLE
    assert menu.move_down() is False and menu.selected is MenuOption.TITLE
    assert menu.move_up() is True and menu.selected is MenuOption.OPTIONS


def test_confirm_returns_selected_option():
    menu = Menu(TITLE_OPTIONS)
    assert menu.confirm() is MenuOption.PLAY
    menu.move_down()
    assert menu.confirm() is MenuOption.RANKING  # 005


# 005 / T005 — entrada de nome (FR-002, FR-003)
def test_name_entry_accepts_letters_digits_and_space_up_to_10():
    entry = NameEntry()
    for ch in "Ana 2":
        assert entry.type(ch) is True
    assert entry.text == "Ana 2"
    for ch in "!é@-":
        assert entry.type(ch) is False
    for ch in "xxxxx":
        entry.type(ch)
    assert len(entry.text) == 10
    assert entry.type("y") is False


def test_name_entry_backspace():
    entry = NameEntry("AB")
    assert entry.backspace() is True and entry.text == "A"
    assert entry.backspace() is True and entry.text == ""
    assert entry.backspace() is False


def test_name_entry_value_strips_and_requires_content():
    entry = NameEntry()
    assert not entry.confirmable
    for ch in "   ":
        entry.type(ch)
    assert not entry.confirmable
    for ch in "BOB ":
        entry.type(ch)
    assert entry.value == "BOB"
    assert entry.confirmable


def test_name_entry_prefill():
    assert NameEntry("ANA").text == "ANA"
