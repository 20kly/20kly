# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
# 

import random

class Game_Random:
    def __init__(self, seed):
        self.rng = random.Random(seed)

    def random(self):
        return self.rng.random()

    def randint(self, a, b):
        return self.rng.randint(a, b)

    def shuffle(self, l):
        self.rng.shuffle(l)

    def reset(self, seed):
        self.rng = random.Random(seed)
        
ui_random = random.Random()
game_random = Game_Random(1)


