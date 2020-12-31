# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 
#
# Here lie various pieces of shared code that 
# don't merit their own modules.


import pygame , sys , time , random

import intersect , bresenham , resource
from primitives import *

# The function returns (x,y), a point on the line between
# (x1,y1) and (x2,y2), such that a / b of the line
# is between (x,y) and (x1,y1).

def Partial_Vector((x1,y1),(x2,y2),(a,b)):
    x = x1 + ((( x2 - x1 ) * a ) / b )
    y = y1 + ((( y2 - y1 ) * a ) / b )
    return (x,y)


# I'm always wanting to sort lists of tuples.
def Sort_By_Tuple_0(list):
    list.sort(cmp=lambda (a,b),(c,d): cmp(a,c))
    return None

def More_Accurate_Line((x1,y1), (x2,y2)):
    def A(i):
        return ( 2 * i ) + 1

    return [ (x / 2, y / 2) for (x,y) in
            bresenham.Line((A(x1), A(y1)), (A(x2), A(y2))) ]

# Check line (a,b) against given grid pos
def Intersect_Grid_Square(gpos, (a,b)):
    (x,y) = gpos
    x -= 0.5
    y -= 0.5
    for (c,d) in [ ((x,y), (x+1,y+1)), ((x+1,y),(x,y+1)) ]:
        if ( intersect.Intersect((a,b), (c,d)) != None ):
            return True

    return False

def Tile_Texture(output, name, rect):
    cr = output.get_clip()
    output.set_clip(rect)

    img = resource.Load_Image(name)
    img_r = img.get_rect()
    for x in range(0, rect.width, img_r.width):
        for y in range(0, rect.height, img_r.height):
            output.blit(img, (x + rect.left, y + rect.top))

    output.set_clip(cr)

def Edge_Effect(output, rect):
    bolt = resource.Load_Image("bolt.png")
    margin = 2
    for x in [ rect.left + margin , rect.right - ( margin + 3 ) ]:
        for y in [ rect.top + margin , rect.bottom - ( margin + 3 ) ]:
            output.blit(bolt, (x,y))

def Line_Edging(screen, r, deflate):
    for c in [ (75, 63, 31), (125, 99, 30), (160, 120, 40), (75, 63, 31), (0, 0, 0) ]:
        pygame.draw.rect(screen, c, r, 1)
        if ( deflate ):
            r = r.inflate(-2,-2)
        else:
            r = r.inflate(2,2)


# Generate start/finish of a quake line.
# Also used by storms.
def Make_Quake_SF_Points(off):
    # Quake fault lines must stay well away from the centre:
    # that's enforced here.
    crosses_centre = True
    (x,y) = GRID_CENTRE
    d = 7
    check = [ (x - d, y - d), (x + d, y + d),
            (x - d, y + d), (x + d, y - d) ]
    (w,h) = GRID_SIZE

    while ( crosses_centre ):
        if ( random.randint(0,1) == 0 ):
            start = (random.randint(0,w - 1), -off)
            finish = (random.randint(0,w - 1), h + off)
        else:
            start = (-off, random.randint(0,h - 1))
            finish = (h + off, random.randint(0,h - 1))

        crosses_centre = ( 
                intersect.Intersect((start, finish),
                    (check[ 0 ], check[ 1 ]))
                or intersect.Intersect((start, finish),
                    (check[ 2 ], check[ 3 ])) )
    return [start, finish]


def Simple_Menu_Loop(screen, current_menu, (x,y)):
    cmd = None
    quit = False

    while (( cmd == None ) and not quit ):
        current_menu.Draw(screen, (x,y))
        pygame.display.flip()

        e = pygame.event.wait()
        while ( e.type != NOEVENT ):
            if e.type == QUIT:
                quit = True
            elif ( e.type == MOUSEBUTTONDOWN ):
                current_menu.Mouse_Down(e.pos)
            elif ( e.type == MOUSEMOTION ):
                current_menu.Mouse_Move(e.pos)
            elif e.type == KEYDOWN:
                current_menu.Key_Press(e.key)
            e = pygame.event.poll()

        cmd = current_menu.Get_Command()
        current_menu.Select(None) # consume 

    return (quit, cmd)


# Support functions.

def Get_OS():
    # On my machine, sys.platform reports 'linux2'. Remove digits.
    pf = sys.platform.title()
    for i in xrange(len(pf)):
        if ( not pf[ i ].isalpha() ):
            pf = pf[0:i]
            break

    if ( pf == 'Win' ):
        pf = 'Windows'
    return pf

def Get_System_Info():
    # Some information about the run-time environment.
    # This gets included in savegames - it may be useful for
    # debugging problems using a savegame as a starting point.
    return repr([time.asctime(), sys.platform, sys.version, 
            pygame.version.ver, sys.path, sys.prefix, sys.executable])

