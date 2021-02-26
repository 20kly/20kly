#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import ctypes


def SDL_SetHintWithPriority(name: str, value: str, priority: int) -> bool:
    try:
        sdl2 = ctypes.CDLL("SDL2")
        fn = sdl2.SDL_SetHintWithPriority
    except Exception:
        return False

    fn.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    fn.restype = ctypes.c_int
    rc = fn(ctypes.create_string_buffer(name.encode("ascii")),
       ctypes.create_string_buffer(value.encode("ascii")),
       priority)
    return rc != 0
