#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


from . import menu, save_game

from .game_types import *

class Save_Menu(menu.Menu):
    def __init__(self, saving: bool) -> None:
        file_list: List[MenuItem] = []

        for slot in save_game.SLOTS:
            label = save_game.Get_Info(slot)
            if ( label is None ):
                x = " " * 10
                label = x + " -- Unused slot -- " + x
                if ( not saving ):
                    slot = MenuCommand.UNUSED # can't load this one! assign silly value

            label = ( "%2d. " % ( save_game.Get_Number(slot) + 1 )) + label

            file_list.append((slot, label, []))

        file_list.append((None, None, []))
        file_list.append((MenuCommand.CANCEL, "Cancel", []))

        self.saving = saving
        menu.Menu.__init__(self, file_list)

    def Is_Saving(self) -> bool:
        return self.saving

    def Justify(self, width: int, text_width: int) -> int:
        return 10

