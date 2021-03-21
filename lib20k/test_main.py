#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from . import main, mail, version, config
from .primitives import *
from .game_types import *
from .unit_test import *



def test_Main_Tutorial() -> None:
    """Unit test for main.py.

    These tests are for options in the main menu.
    Start the tutorial and then quit. Correctness checked
    by looking at in-game mail."""
    config.cfg.Reset()
    config.Save()
    event_list = [Push(pygame.K_t), # tutorial
                  NoEvent(),
                  NoEvent(),
                  NoEvent(),
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[], event=Fake_Events(event_list))
    assert "You are playing a Tutorial game" in mail.Get_Messages()

def test_Main_Peaceful_Save() -> None:
    """start a Peaceful game and do a save game,
    then restore it. Correctness checked by looking
    at in-game mail."""
    event_list = [NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  VideoResize(),
                  NoEvent(),
                  Push(pygame.K_p), # peaceful
                  NoEvent(),
                  Push(pygame.K_ESCAPE), # open in-game menu
                  NoEvent(),
                  VideoResize(),
                  NoEvent(),
                  Push(pygame.K_s), # open save menu
                  NoEvent(),
                  NoEvent(),
                  NoEvent(),
                  Push(pygame.K_9), # save slot 9
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=["--no-sound"],
              event=Fake_Events(event_list))
    peaceful = "You are playing a Peaceful game" 
    assert peaceful in mail.Get_Messages()
    assert "Game saved" in mail.Get_Messages()

    # now restore the save game - check restore message
    event_list = [NoEvent(),
                  Push(pygame.K_r), # open restore menu
                  NoEvent(),
                  VideoResize(),
                  NoEvent(),
                  Push(pygame.K_9), # restore slot 9
                  NoEvent(),
                  Push(pygame.K_F6), # win the game
                  NoEvent(),
                  NoEvent(),
                  NoEvent(),
                  NoEvent(),
                  NoEvent(),
                  Push(pygame.K_r),  # review stats
                  NoEvent(),
                  Push(pygame.K_ESCAPE),
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[],
              event=Fake_Events(event_list))
    assert peaceful in mail.Get_Messages()
    assert "GAME END CHEAT (WIN)" in mail.Get_Messages()
    assert "You have won the game" in mail.Get_Messages()

    # restore the save game from within the game - check restore message
    event_list = [NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_e), # expert
                  NoEvent(),
                  Push(pygame.K_ESCAPE), # open menu
                  NoEvent(),
                  Push(pygame.K_r), # open restore menu
                  NoEvent(),
                  VideoResize(),
                  NoEvent(),
                  Push(pygame.K_9), # restore slot 9
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[],
              event=Fake_Events(event_list))
    assert "Game restored" in mail.Get_Messages()
    assert peaceful in mail.Get_Messages()

def test_Main_Record() -> None:
    """Start a game with recording."""
    event_list = [NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=["--record", "tmp/test.tmp"],
              event=Fake_Events(event_list))
    assert "You are playing a Beginner game" in mail.Get_Messages()

def test_Main_Options() -> None:
    """Test other options on the menu: mute, updates."""
    # do some menu options on the main menu
    event_list = [Push(pygame.K_m), # mute
                  NoEvent(),
                  Push(pygame.K_m), # unmute
                  NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_ESCAPE), # cancel
                  NoEvent(),
                  Push(pygame.K_r), # restore game
                  NoEvent(),
                  Push(pygame.K_ESCAPE), # cancel
                  NoEvent(),
                  Push(pygame.K_u), # update button
                  NoEvent(),
                  Other(),
                  Click((0, 0)), # cancel
                  NoEvent(),
                  Push(pygame.K_v), # manual button
                  NoEvent(),
                  Push(pygame.K_ESCAPE), # exit
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[], event=Fake_Events(event_list))
    assert "CHECK UPDATE URL http://" in mail.Get_Messages()
    assert "LYU.cgi?a=" in mail.Get_Messages()
    assert "OPEN URL http://" in mail.Get_Messages()
    assert "LYU.cgi?v=" in mail.Get_Messages()
    assert "index.html" in mail.Get_Messages()


class Fake_Update_Events(Fake_Events):
    def __init__(self, action: typing.Callable[[str], str]) -> None:
        Fake_Events.__init__(self, [
                  Push(pygame.K_u), # update button
                  NoEvent(),
                  Click((0, 0)),    # cancel
                  NoEvent(),
                  Quit(),
                  NoEvent()])
        self.action = action

    def check_update(self, url: str) -> str:
        return self.action(url)

def test_Update_Feature() -> None:
    """Test the update feature. Checks various types of failure
    by hooking both sides of the API."""

    def No_Update_1(url: str) -> str:
        return version.Encode(VERSION)

    main.Main(data_dir="data", args=[], event=Fake_Update_Events(No_Update_1))
    assert not ("OPEN URL" in mail.Get_Messages())

    def No_Update_2(url: str) -> str:
        return "1.0"

    main.Main(data_dir="data", args=[], event=Fake_Update_Events(No_Update_2))
    assert not ("OPEN URL" in mail.Get_Messages())

    def Bad_Update_1(url: str) -> str:
        raise Exception("hello")

    main.Main(data_dir="data", args=[], event=Fake_Update_Events(Bad_Update_1))
    assert not ("OPEN URL" in mail.Get_Messages())

    def Bad_Update_2(url: str) -> str:
        return "x.x"

    main.Main(data_dir="data", args=[], event=Fake_Update_Events(Bad_Update_2))
    assert not ("OPEN URL" in mail.Get_Messages())
