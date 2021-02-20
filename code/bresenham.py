# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 



# Line drawing algorithm. Produces a list. This is useful for all sorts
# of linear interpolations.
#
# Page 78, Computer Graphics Principles and Practice (2nd. Ed), Foley et al.

def Line(arg1, arg2):
    (x1,y1) = arg1
    (x2,y2) = arg2
   
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    dx = x2 - x1
    dy = y2 - y1

    if ( abs(dx) < abs(dy) ):
        # Gradient is steeper than 1. Correct this.
        return [ (x,y) for (y,x) in Line((y1,x1),(y2,x2)) ]

    if ( dx < 0 ):
        # Line is reversed. Correct this.
        l = Line((x2,y2),(x1,y1))
        l.reverse()
        return l

    if ( dy < 0 ):
        direction = -1
        dy = - dy
    else:
        direction = 1

    d = ( 2 * dy ) - dx
    incr_e = 2 * dy
    incr_ne = 2 * ( dy - dx )
    y = y1
    l = [(x1,y)]

    for x in range(x1, x2 + 1):
        if ( d <= 0 ):
            d += incr_e # move east
        else:
            d += incr_ne # move northeast
            y += direction
        l.append((x,y))
    
    if ( y != y2 ):
        l.append((x2,y2))

    return l


