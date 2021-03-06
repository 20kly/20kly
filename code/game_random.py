#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import random
import tempfile
import struct
import bz2
import math

from . import map_items
from . import steam_model
from . import game
from . import ui
from .primitives import *
from .game_types import *

READ_HEADER_NUMBER = 20210214
WRITE_HEADER_NUMBER = 20210214

class Game_Random:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.rng: Optional[random.Random] = random.Random(seed)
        self.record: Optional[bz2.BZ2File] = None
        self.play: Optional[typing.IO[bytes]] = None

    def random(self) -> float:
        assert self.rng is not None
        x = self.rng.random()
        if self.play:
            (x, ) = self.read_specific("RANDOM", "<d")

        if self.record: # NO-COV
            self.write_specific("RANDOM", "<d", x)

        return x

    def randint(self, a: int, b: int) -> int:
        assert self.rng is not None
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

    def shuffle(self, l: List[typing.Any]) -> None:
        self.read_and_write("SHUFFLE", "<I", len(l))
        for i in range(1, len(l)):
            j = self.randint(0, i)
            (l[i], l[j]) = (l[j], l[i])

    def begin_write(self, recording_file: str, challenge: MenuCommand) -> None:
        self.record = bz2.BZ2File(recording_file, "wb")
        seed = random.randint(1, 1 << 31)
        self.write_specific("GAME", "<I", WRITE_HEADER_NUMBER)
        self.write_specific("SEED", "<II", seed, challenge.value)
        self.rng = random.Random(seed)

    def begin_read(self, recording_file: str) -> MenuCommand:
        self.play = tempfile.NamedTemporaryFile()
        self.play.write(bz2.BZ2File(recording_file, "rb").read())
        self.play.seek(0, 0)
        (header, ) = self.read_specific("GAME", "<I")
        assert header == READ_HEADER_NUMBER
        (seed, challenge) = self.read_specific("SEED", "<II")
        self.rng = random.Random(seed)
        return MenuCommand(challenge)

    def do_user_actions(self, ui: "ui.User_Interface") -> None:
        if not self.play:
            return

        (name, payload) = self.peek_any()
        while name.startswith("ACTION_"):
            if self.record: # NO-COV
                self.read_and_write(name,
                            "<" + str(len(payload)) + "s", payload)
            else:
                self.read_any()

            name = name[7:]
            object_data = struct.unpack("<" + str(len(payload)) + "B", payload)
            ui.Playback_Action(name, *object_data)
            (name, payload) = self.peek_any()

    def timestamp(self, g: "game.Game_Data") -> None:
        supply = g.net.hub.Get_Steam_Supply()
        demand = g.net.hub.Get_Steam_Demand()
        bad = []
        grid_locs = sorted(set(g.net.pipe_grid) | set(g.net.ground_grid))
        self.read_and_write("TIMESTAMP", "<dddI", g.game_time.time(), supply, demand, len(grid_locs))

        for pos in grid_locs:
            (x2, y2) = pos
            pipes = g.net.pipe_grid.get(pos, [])
            node = g.net.ground_grid.get(pos, None)
            if isinstance(node, map_items.Well_Node):
                node_code = 1
            elif isinstance(node, map_items.Node):
                node_code = 2
            elif isinstance(node, map_items.Well):
                node_code = 3
            else:
                node_code = 0

            g.net.Remove_Destroyed_Pipes(pos)
            try:
                self.read_and_write("G", "<BBBB", x2, y2, len(pipes), node_code)
            except PlaybackError as e: # NO-COV
                bad.append(str(e))

            for pipe in sorted(pipes, key=lambda pipe: (pipe.n1.pos, pipe.n2.pos)):
                (x1, y1) = pipe.n1.pos
                (x3, y3) = pipe.n2.pos
                try:
                    self.read_and_write("P", "<BBBB", x1, y1, x3, y3)
                except PlaybackError as e: # NO-COV
                    bad.append(str(e))
            if 1 <= node_code <= 2:
                assert isinstance(node, map_items.Node)
                try:
                    self.read_and_write("N", "<id",
                                        node.health, node.steam.charge)
                except PlaybackError as e: # NO-COV
                    bad.append(str(e))

            if len(bad):    # NO-COV
                for pipe in sorted(pipes, key=lambda pipe: (pipe.n1.pos, pipe.n2.pos)):
                    bad.append("\nexpected pipe: " +
                            repr((pipe.n1.pos, pipe.n2.pos,
                                pipe.destroyed, pipe.health)) + "\n")
                raise PlaybackError("".join(bad))

    def Action(self, name, *objects) -> None:       # NO-COV
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

    def Steam(self, neighbour_list: List[Tuple[steam_model.Steam_Model, float]],
              voltage: float, charge: float, capacitance: float,
              currents: List[float]):
        assert len(neighbour_list) == len(currents)
        self.read_and_write("ST", "<Iddd",
                    len(neighbour_list),
                    voltage, charge, capacitance)
        for i in range(len(neighbour_list)):
            (neighbour, resist) = neighbour_list[i]
            self.read_and_write("n", "<dd", resist, currents[i])

    def Pre_Save(self) -> None:
        self.record = None
        self.play = None
        self.rng = None

    def Post_Load(self) -> None:
        self.rng = random.Random()

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
            if readback != data:        # NO-COV
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
        if len(header) != 2: # NO-COV
            raise PlaybackError("When reading packet header at 0x%x - unexpected EOF" % loc)

        (len_name, len_payload) = struct.unpack("<BB", header)
        name = self.play.read(len_name).decode("utf-8")
        payload = self.play.read(len_payload)
        if len(payload) != len_payload: # NO-COV
            raise PlaybackError("When reading packet payload at 0x%x - unexpected EOF" % loc)

        return (name, payload)

    def read_specific(self, name, fmt):
        loc = self.play.tell()
        (read_name, read_payload) = self.read_any()

        if read_name != name: # NO-COV
            raise PlaybackError("When reading packet at 0x%x, name did not match:\n"
                                "expected name '%s'\n"
                                "actually read '%s'\n" % (loc, name, read_name))

        try:
            return struct.unpack(fmt, read_payload)
        except Exception: # NO-COV
            raise PlaybackError("When reading packet at 0x%x, name '%s' matched, but "
                                "payload was not decoded" % (loc, name))


class PlaybackError(Exception):
    pass

class PlaybackEOF(Exception):
    pass
