# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
# 

import random
import tempfile
import struct
import map_items

class Game_Random:
    def __init__(self):
        self.rng = random.Random()
        self.record = tempfile.NamedTemporaryFile()

    def random(self):
        x = self.rng.random()
        self.write("RANDOM", "<d", x)
        return x

    def randint(self, a, b):
        x = self.rng.randint(a, b)
        assert a <= x <= b
        assert abs(a) <= (1 << 31)
        assert abs(b) <= (1 << 31)
        self.write("RANDINT", "<iii", a, b, x)
        return x

    def shuffle(self, l):
        self.write("SHUFFLE", "<I", len(l))
        for i in range(1, len(l)):
            j = self.randint(0, i)
            (l[i], l[j]) = (l[j], l[i])

    def reset(self, seed):
        self.record = tempfile.NamedTemporaryFile()
        self.write("SEED", "<i", seed)
        self.rng = random.Random(seed)

    def begin(self, recording_file):
        self.record = open(recording_file, "wb")
        self.interval = 0
        self.write("GAME", "<I", 20210101)

    def work_timer_event(self, g):
        self.write("WORK_TIMER_EVENT", "")
        for n in g.net.node_list:
            (x, y) = n.pos
            self.write("NODE", "<iiid", x, y, n.health, n.steam.charge)
        #pickle.dump(g,f)

    def action(self, name, *objects):
        object_data = []
        for obj in objects:
            if type(obj) == tuple:
                (x, y) = obj
                object_data.append(x)
                object_data.append(y)
            elif isinstance(obj, map_items.Building):
                (x, y) = obj.pos
                object_data.append(x)
                object_data.append(y)
            else:
                assert False, repr(obj)

        self.write("ACTION_" + name, "<" + str(len(object_data)) + "i", *object_data)

    def write(self, name, fmt, *data):
        payload = struct.pack(fmt, *data)
        header = struct.pack("<II", len(name), len(payload))
        #self.record.write(header)
        #self.record.write(name)
        #self.record.write(payload)
        self.record.write(name + " " + repr(data) + "\n")

ui_random = random.Random()
game_random = Game_Random()


