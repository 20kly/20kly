#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

from . import game_random, game, save_game, unit_test
from . import mail
from .ui import User_Interface
from .primitives import *
from .unit_test import *


def test_Save_Restore() -> None:
    """Test for save_game.py.

    This is a test of the actual savegame feature. We set up
    a fake game, save it, restore it, and also try restoring
    nonsense. Checked using assertions."""

    test_screen = unit_test.Setup_For_Unit_Test()
    demo = game_random.Game_Random(1)
    clock = pygame.time.Clock()
    game_loop = game.Game(clock=clock,
                    restore_pos=None,
                    challenge=MenuCommand.INTERMEDIATE, event=Fake_Events([]),
                    playback_mode=PlayMode.OFF,
                    playback_file=None,
                    record_file=None)
    g = game_loop.g
    ui = game_loop.ui
    assert ui.net == g.net
    g.historian_time = 999.0

    assert g.net.demo.random() >= -1.0      # check that random numbers can be generated
    result = save_game.Save(g, MenuCommand.SAVE9, "test save")
    assert result is None
    assert g.net.demo.random() >= -1.0
    g.historian_time = 123.0

    g2 = game_loop.Restore(MenuCommand.SAVE9)
    assert g2 != g
    assert g2.net != g.net                  # network reloaded
    assert ui.net == g2.net                 # ui is updated correctly
    assert g2.historian_time == 999.0       # value restored correctly
    assert g2.net.demo.random() >= -1.0
    assert "Game restored" in mail.Get_Messages()
    g = g2

    # Overwrite save game with nonsense
    name = save_game.Make_Save_Name(MenuCommand.SAVE9)
    open(name, "wb").write(b"INVALID")

    # Try restoring - doesn't work
    g2 = game_loop.Restore(MenuCommand.SAVE9)
    assert g2 == g      # No reload
    assert "Error restoring file" in mail.Get_Messages()
