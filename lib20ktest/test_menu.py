#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from lib20k import events, menu
from lib20k.primitives import *
from lib20k.game_types import *
from .unit_test import *


def test_Simple_Menu_Loop() -> None:
    """Test for menu.py.

    Generate test menus and send fake keyboard/mouse events.
    One of the many reasons to NOT create your own GUI widgets
    is that you eventually have to write tests like this."""

    test_screen = Setup_For_Unit_Test()
    menu_options: List[MenuItem] = [
            (MenuCommand.SAVE0, "TEST0", [pygame.K_0]),
            (None, None, []),
            (MenuCommand.SAVE1, "TEST1", [pygame.K_1]),
            (MenuCommand.SAVE2, "TEST2", []),
            (MenuCommand.SAVE3, "TEST3", [pygame.K_3, pygame.K_x]),
        ]

    # test quit by closing the window
    test_menu = menu.Menu(menu_options, force_width=0)
    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events([
                            Quit(),
                            NoEvent()
                        ]))
    assert quit
    assert cmd is None

    # test video resize
    test_menu = menu.Menu(menu_options, force_width=0)
    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events([
                            VideoResize(),
                            NoEvent(),
                            Quit(),
                            NoEvent()
                        ]))
    assert not quit
    assert cmd is None

    # test keypresses
    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events([
                            Push(pygame.K_1),
                            NoEvent()
                        ]))
    assert not quit
    assert cmd == MenuCommand.SAVE1
    assert test_menu.hover is None
    assert test_menu.Get_Command() is None

    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events([
                            Push(pygame.K_a), # ignored (not valid)
                            Other(),
                            NoEvent(),
                            NoEvent(),
                            Push(pygame.K_x), # accepted
                            NoEvent(),
                            Quit(),           # not reached
                            NoEvent(),
                        ]))
    assert not quit
    assert cmd == MenuCommand.SAVE3

    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events([
                            Push(pygame.K_3),   # accepted
                            NoEvent(),
                            Push(pygame.K_1),   # not reached
                            NoEvent()
                        ]))
    assert not quit
    assert cmd == MenuCommand.SAVE3

    # test mouse movements - hover over each option
    event_list: List[events.Event] = [
                Move(r.center) for (_, r) in test_menu.control_rects]
    event_list.append(NoEvent())
    event_list.append(Quit())
    event_list.append(NoEvent())
    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events(event_list))
    assert cmd is None
    assert quit
    assert test_menu.hover == MenuCommand.SAVE3

    # recreate menu with a header and forced size (to test these options)
    menu_options.insert(0, (None, None, []))
    test_menu = menu.Menu(menu_options, force_width=200)
    save2_pos = test_menu.control_rects[2][1].center

    # test mouse click - select an option
    event_list = [Click(save2_pos), NoEvent()]
    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events(event_list))
    assert cmd == MenuCommand.SAVE2
    assert not quit

    # test mouse movement outside the box
    event_list = [NoEvent(),
                  NoEvent(),
                  Move((-1, -1)),   # outside box
                  Click((-1, -1)),
                  Move((0, 0)),     # within box but outside rects
                  Move(save2_pos),
                  Move(save2_pos),
                  Move((-1, -1))]
    event_list.append(NoEvent())
    event_list.append(Quit())
    event_list.append(NoEvent())
    (quit, cmd) = menu.Simple_Menu_Loop(test_screen, test_menu,
                        (0, 0), Fake_Events(event_list))
    assert cmd is None
    assert quit
    assert test_menu.hover is None

    # force drawing a selection
    test_menu.Select(MenuCommand.SAVE1)
    test_menu.Draw(test_screen)

    # force drawing when no update required
    test_menu.Draw(test_screen)

    # Add a picture to some item
    test_menu = menu.Enhanced_Menu(menu_options, force_width=200,
                        pictures={
                            MenuCommand.SAVE1: Images.bricks
                        })
    test_menu.Draw(test_screen)

