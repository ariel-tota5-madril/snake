from snake.menu import EndMenu, MenuOption


# T032
def test_menu_starts_on_restart():
    menu = EndMenu()
    assert menu.options == (MenuOption.RESTART, MenuOption.QUIT)
    assert menu.selected is MenuOption.RESTART


def test_move_down_selects_quit_and_stops_at_the_end():
    menu = EndMenu()
    menu.move_down()
    assert menu.selected is MenuOption.QUIT
    menu.move_down()
    assert menu.selected is MenuOption.QUIT


def test_move_up_stops_at_the_top():
    menu = EndMenu()
    menu.move_up()
    assert menu.selected is MenuOption.RESTART
    menu.move_down()
    menu.move_up()
    assert menu.selected is MenuOption.RESTART


def test_confirm_returns_selected_option():
    menu = EndMenu()
    assert menu.confirm() is MenuOption.RESTART
    menu.move_down()
    assert menu.confirm() is MenuOption.QUIT
