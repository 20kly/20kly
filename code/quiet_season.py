# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

class Quiet_Season:
    # The quiet season is... very quiet.
    def __init__(self, net):
        self.net = net
        self.name = "Quiet"

    def Per_Frame(self, frame_time):
        pass

    def Per_Period(self):
        pass
        
    def Draw(self, output, update_area):
        pass

    def Get_Period(self):
        return 10
        
    def Get_Extra_Info(self):
        return []

    def Is_Shaking(self):
        return False


