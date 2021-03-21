#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


from .game_types import *


def Decode(version: str) -> VersionType:
    version_code = version.strip().split(".")
    incr = 0
    try:
        major = int(version_code[0], 10)
        minor = int(version_code[1], 10)
        if len(version_code) > 2:
            incr = int(version_code[2], 10)
        return (major, minor, incr)

    except Exception as x: # NO-COV
        return (0, 0, 0)

def Encode(version_int: VersionType) -> str:
    return "{}.{}.{}".format(*version_int)

