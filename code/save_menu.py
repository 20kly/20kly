#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#


from . import menu, save_game

from .game_types import *

KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
        pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
        pygame.K_9, pygame.K_0]

class Save_Menu(menu.Menu):
    def __init__(self, saving: bool) -> None:
        file_list: List[MenuItem] = []
        slot: Optional[MenuCommand] = None

        for (number, (slot, key)) in enumerate(zip(save_game.SLOTS, KEYS)):
            assert slot is not None
            label = save_game.Get_Info(slot)
            if ( label is None ):
                x = " " * 10
                label = x + " -- Unused slot -- " + x
                if ( not saving ):
                    slot = None # can't load this one! assign silly value

            label = ("%2d. " % (number + 1)) + label

            file_list.append((slot, label, [key]))

        file_list.append((None, None, []))
        file_list.append((MenuCommand.CANCEL, "Cancel", [pygame.K_ESCAPE]))

        self.saving = saving
        menu.Menu.__init__(self, file_list)

    def Is_Saving(self) -> bool:
        return self.saving

    def Justify(self, width: int, text_width: int) -> int:
        return 10

