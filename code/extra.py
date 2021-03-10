#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
#
#
# Here lie various pieces of shared code that
# don't merit their own modules.


import pygame, sys, time, os

from . import intersect, resource
from . import menu
from .primitives import *
from .game_types import *
from . import game_random

# The function returns (x,y), a point on the line between
# (x1,y1) and (x2,y2), such that a / b of the line
# is between (x,y) and (x1,y1).

def Partial_Vector(arg1: FloatSurfacePosition, arg2: FloatSurfacePosition,
                   arg3: Tuple[float, float]) -> FloatSurfacePosition:
    (x1,y1) = arg1
    (x2,y2) = arg2
    (a,b) = arg3
    x = x1 + ((( x2 - x1 ) * a ) / b )
    y = y1 + ((( y2 - y1 ) * a ) / b )
    return (x,y)


# I'm always wanting to sort lists of tuples.
def Sort_By_Tuple_0(list_of_tuples: List[typing.Any]) -> None:
    list_of_tuples.sort(key=lambda x: x[0])
    return None

def Tile_Texture(output: SurfaceType, name: str, rect: RectType) -> None:
    cr = output.get_clip()
    output.set_clip(rect)

    img = resource.Load_Image(name)
    img_r = img.get_rect()
    for x in range(0, rect.width, img_r.width):
        for y in range(0, rect.height, img_r.height):
            output.blit(img, (x + rect.left, y + rect.top))

    output.set_clip(cr)

def Edge_Effect(output: SurfaceType, rect: RectType) -> None:
    bolt = resource.Load_Image("bolt.png")
    margin = 2
    for x in [ rect.left + margin , rect.right - ( margin + 3 ) ]:
        for y in [ rect.top + margin , rect.bottom - ( margin + 3 ) ]:
            output.blit(bolt, (x,y))

def Line_Edging(screen: SurfaceType, r: RectType, deflate: bool) -> None:
    for c in [ (75, 63, 31), (125, 99, 30), (160, 120, 40), (75, 63, 31), (0, 0, 0) ]:
        pygame.draw.rect(screen, c, r, 1)
        if ( deflate ):
            r = r.inflate(-2,-2)
        else:
            r = r.inflate(2,2)

def List_Destroy(lst: List[typing.Any], itm: typing.Any) -> None:
    if itm in lst:
        lst.remove(itm)

# Generate start/finish of a quake line.
# Also used by storms.
def Make_Quake_SF_Points(demo: "game_random.Game_Random", off: int) -> List[SurfacePosition]:
    # Quake fault lines must stay well away from the centre:
    # that's enforced here.
    crosses_centre = True
    (x,y) = GRID_CENTRE
    d = 7
    check = [ (x - d, y - d), (x + d, y + d),
            (x - d, y + d), (x + d, y - d) ]
    (w,h) = GRID_SIZE

    while ( crosses_centre ):
        if ( demo.randint(0,1) == 0 ):
            start = (demo.randint(0,w - 1), -off)
            finish = (demo.randint(0,w - 1), h + off)
        else:
            start = (-off, demo.randint(0,h - 1))
            finish = (h + off, demo.randint(0,h - 1))

        crosses_centre = (intersect.Lines_Intersect((start, finish), (check[0], check[1]))
                or intersect.Lines_Intersect((start, finish), (check[2], check[3])))
    return [start, finish]


# Support functions.

def Get_System_Info() -> str:
    # Some information about the run-time environment.
    # This gets included in savegames - it may be useful for
    # debugging problems using a savegame as a starting point.
    return repr([time.asctime(), sys.platform, sys.version,
            pygame.version.ver, sys.path, sys.prefix, sys.executable])


def Get_Home() -> Optional[str]:
    for i in [ "HOME", "APPDATA" ]:     # NO-COV
        home = os.getenv(i)             # NO-COV
        if ( home is not None ):        # NO-COV
            return home                 # NO-COV
    return None                         # NO-COV

