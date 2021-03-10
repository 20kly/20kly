# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
# 

import random
import tempfile
import struct
import map_items
import bz2
import math

READ_HEADER_NUMBER = 20210307
WRITE_HEADER_NUMBER = 20210307

class Game_Random:
    def __init__(self):
        self.rng = random.Random()
        self.record = None
        self.play = None

    def random(self):
        x = self.rng.random()
        if self.play:
            (x, ) = self.read_specific("RANDOM", "<d")

        if self.record:
            self.write_specific("RANDOM", "<d", x)

        return x

    def randint(self, a, b):
        x = self.rng.randint(a, b)
        assert a <= x <= b
        assert abs(a) <= (1 << 31)
        assert abs(b) <= (1 << 31)

        if self.play:
            (ra, rb, x) = self.read_specific("RANDINT", "<iii")
            assert a == ra
            assert b == rb
            assert a <= x <= b

        if self.record:
            self.write_specific("RANDINT", "<iii", a, b, x)

        return x

    def shuffle(self, l):
        self.read_and_write("SHUFFLE", "<I", len(l))
        for i in range(1, len(l)):
            j = self.randint(0, i)
            (l[i], l[j]) = (l[j], l[i])

    def begin_write(self, recording_file, challenge):
        self.record = bz2.BZ2File(recording_file, "wb")
        seed = ui_random.randint(1, 1 << 31)
        self.write_specific("GAME", "<I", WRITE_HEADER_NUMBER)
        self.write_specific("SEED", "<II", seed, challenge)
        self.rng = random.Random(seed)

    def begin_read(self, recording_file):
        self.play = tempfile.NamedTemporaryFile()
        self.play.write(bz2.BZ2File(recording_file, "rb").read())
        self.play.seek(0, 0)
        (header, ) = self.read_specific("GAME", "<I")
        assert header == READ_HEADER_NUMBER
        (seed, challenge) = self.read_specific("SEED", "<II")
        self.rng = random.Random(seed)
        return challenge

    def do_user_actions(self, ui):
        if not self.play:
            return

        while True:
            (name, payload) = self.peek_any()
            if name.startswith("ACTION_"):
                if self.record:
                    self.read_and_write(name,
                                "<" + str(len(payload)) + "s", payload)
                else:
                    self.read_any()
                name = name[7:]
                object_data = struct.unpack("<" + str(len(payload)) + "B", payload)
                ui.Playback_Action(name, *object_data)
            else:
                break

    def timestamp(self, g):
        supply = g.net.hub.Get_Steam_Supply()
        demand = g.net.hub.Get_Steam_Demand()

        self.read_and_write("TS", "<dddIII", g.game_time.time(), supply, demand,
                             len(g.net.well_list), len(g.net.node_list), len(g.net.pipe_list))

        for well in sorted(g.net.well_list, key=lambda well: well.pos):
            assert isinstance(well, map_items.Well)
            (x2, y2) = well.pos
            self.read_and_write("W", "<BB", x2, y2)

        for node in sorted(g.net.node_list, key=lambda node: node.pos):
            if isinstance(node, map_items.Well_Node):
                node_code = 1
            else:
                assert isinstance(node, map_items.Node)
                node_code = 2
            (x2, y2) = node.pos
            self.read_and_write("N", "<BBBid", x2, y2, node_code, node.health, node.steam.charge)

        for pipe in sorted(g.net.pipe_list, key=lambda pipe: (pipe.n1.pos, pipe.n2.pos)):
            (x1, y1) = pipe.n1.pos
            (x3, y3) = pipe.n2.pos
            self.read_and_write("P", "<BBBBd", x1, y1, x3, y3, pipe.current_n1_to_n2)

    def Action(self, name, *objects):
        object_data = []
        for obj in objects:
            if isinstance(obj, map_items.Pipe):
                (x, y) = obj.n1.pos
                object_data.append(x)
                object_data.append(y)
                (x, y) = obj.n2.pos
                object_data.append(x)
                object_data.append(y)
            elif isinstance(obj, map_items.Building):
                (x, y) = obj.pos
                object_data.append(x)
                object_data.append(y)
            else:
                assert False, repr(obj)

        self.read_and_write("ACTION_" + name, "<" + str(len(object_data)) + "B", *object_data)

    def Steam(self, neighbour_list, voltage, charge, capacitance, currents):
        assert len(neighbour_list) == len(currents)
        self.read_and_write("ST", "<Iddd",
                    len(neighbour_list),
                    voltage, charge, capacitance)
        for i in range(len(neighbour_list)):
            (neighbour, resist) = neighbour_list[i]
            self.read_and_write("n", "<dd", resist, currents[i])

    def hypot(self, dy, dx):
        result = math.hypot(dy, dx)

        if self.play:
            (readback_dy, readback_dx, result) = self.read_specific("HYP", "<ddd")
            assert readback_dy == dy
            assert readback_dx == dx

        if self.record:
            self.write_specific("HYP", "<ddd", dy, dx, result)

        return result

    def read_and_write(self, name, fmt, *data):
        if self.play:
            loc = self.play.tell()
            readback = self.read_specific(name, fmt)
            if readback != data:
                raise PlaybackError("When reading packet at 0x%x, name '%s' matched, "
                                    "but data did not:\n"
                                    "expected data %s\n"
                                    "actually read %s\n" % (loc, name, repr(data), repr(readback)))

        if self.record:
            self.write_specific(name, fmt, *data)

    def write_specific(self, name, fmt, *data):
        assert self.record
        name_bytes = name.encode("utf-8")
        payload = struct.pack(fmt, *data)
        header = struct.pack("<BB", len(name_bytes), len(payload))
        self.record.write(header)
        self.record.write(name_bytes)
        self.record.write(payload)

    def peek_any(self):
        assert self.play
        loc = self.play.tell()
        (name, payload) = self.read_any()
        self.play.seek(loc, 0)
        return (name, payload)

    def read_any(self):
        assert self.play
        loc = self.play.tell()
        header = self.play.read(2)
        if len(header) == 0:
            raise PlaybackEOF()
        if len(header) != 2:
            raise PlaybackError("When reading packet header at 0x%x - unexpected EOF" % loc)

        (len_name, len_payload) = struct.unpack("<BB", header)
        name = self.play.read(len_name).decode("utf-8")
        payload = self.play.read(len_payload)
        if len(payload) != len_payload:
            raise PlaybackError("When reading packet payload at 0x%x - unexpected EOF" % loc)

        return (name, payload)

    def read_specific(self, name, fmt):
        loc = self.play.tell()
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


