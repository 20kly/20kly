# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
# 

import random
import tempfile
import struct
import map_items

HEADER_NUMBER = 20210101

class Game_Random:
    def __init__(self):
        self.rng = random.Random()
        self.record = tempfile.NamedTemporaryFile()
        self.reading = False

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

    def begin_write(self, recording_file):
        self.reading = False
        self.record = open(recording_file, "wb")
        seed = ui_random.randint(1, 1 << 31)
        self.write("GAME", "<I", HEADER_NUMBER)
        self.write("SEED", "<i", seed)
        self.rng = random.Random(seed)

    def begin_read(self, recording_file):
        self.reading = True
        self.record = open(recording_file, "rb")
        self.write("GAME", "<I", HEADER_NUMBER)
        (seed, ) = self.read_specific("SEED", "<i")
        self.rng = random.Random(seed)

    def do_user_actions(self, ui):
        if not self.reading:
            return
        while True:
            (name, payload) = self.peek_any()
            if name.startswith("ACTION_"):
                self.read_any()
                name = name[7:]
                assert (len(payload) % 4) == 0
                words = len(payload) // 4
                assert (0 <= words <= 4)
                object_data = struct.unpack("<" + str(words) + "i", payload)
                ui.Playback_Action(name, *object_data)
            else:
                break

    def timestamp(self, g):
        supply = g.net.hub.Get_Steam_Supply()
        demand = g.net.hub.Get_Steam_Demand()
        self.write("TS", "<ddd", g.game_time.time(), supply, demand)
        for n in g.net.node_list:
            (x, y) = n.pos
            self.write("NODE", "<iiid", x, y, n.health, n.steam.charge)

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
        if self.reading:
            loc = self.record.tell()
            readback = self.read_specific(name, fmt)
            if readback != data:
                raise PlaybackError("When reading packet at 0x%x, name '%s' matched, "
                                    "but data did not:\n"
                                    "expected data %s\n"
                                    "actually read %s\n" % (loc, name, repr(data), repr(readback)))
            return

        name_bytes = name.encode("utf-8")
        payload = struct.pack(fmt, *data)
        header = struct.pack("<II", len(name_bytes), len(payload))
        self.record.write(header)
        self.record.write(name_bytes)
        self.record.write(payload)

    def peek_any(self):
        loc = self.record.tell()
        (name, payload) = self.read_any()
        self.record.seek(loc, 0)
        return (name, payload)

    def read_any(self):
        loc = self.record.tell()
        header = self.record.read(8)
        if len(header) == 0:
            raise PlaybackEOF()
        if len(header) != 8:
            raise PlaybackError("When reading packet header at 0x%x - unexpected EOF" % loc)

        (len_name, len_payload) = struct.unpack("<II", header)
        name = self.record.read(len_name).decode("utf-8")
        payload = self.record.read(len_payload)
        if len(payload) != len_payload:
            raise PlaybackError("When reading packet payload at 0x%x - unexpected EOF" % loc)

        return (name, payload)

    def read_specific(self, name, fmt):
        loc = self.record.tell()
        (read_name, read_payload) = self.read_any()

        if read_name != name:
            raise PlaybackError("When reading packet at 0x%x, name did not match:\n"
                                "expected name '%s'\n"
                                "actually read '%s'\n" % (loc, name, read_name))

        try:
            return struct.unpack(fmt, read_payload)
        except Exception:
            raise PlaybackError("When reading packet at 0x%x, name '%s' matched, but "
                                "payload was not decoded" % (loc, name))


class PlaybackError(Exception):
    pass

class PlaybackEOF(Exception):
    pass

ui_random = random.Random()
game_random = Game_Random()


