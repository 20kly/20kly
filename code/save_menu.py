# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 


import menu, save_game


class Save_Menu(menu.Menu):
    def __init__(self, saving):
        file_list = []

        for i in xrange(save_game.NUM_SLOTS):
            label = save_game.Get_Info(i)
            j = i
            if ( label == None ):
                x = " " * 10
                label = x + " -- Unused slot -- " + x
                if ( not saving ):
                    j = - ( i + 100 ) # can't load this one! assign silly value

            label = ( "%2d. " % ( i + 1 )) + label

            file_list.append((j, label, []))

        file_list.append((None, None, []))
        file_list.append((-1, "Cancel", []))
        
        self.saving = saving
        menu.Menu.__init__(self, file_list)

    def Is_Saving(self):
        return self.saving

    def Justify(self, width, text_width):
        return 10

