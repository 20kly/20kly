# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 


# Line intersection algorithm. Thanks to page 113 of
# Computer Graphics Principles and Practice (2nd. Ed), Foley et al.
#
# Note 1: it's not an intersection if the two lines share an endpoint.
# Note 2: Can't detect overlapping parallel lines.

def Intersect(((xa1,ya1),(xa2,ya2)),((xb1,yb1),(xb2,yb2))):
    xa = xa2 - xa1
    ya = ya2 - ya1
    xb = xb2 - xb1
    yb = yb2 - yb1

    a = ( xa * yb ) - ( xb * ya )
    if ( a == 0 ):
        return None

    b = ((( xa * ya1 ) + ( xb1 * ya ) - ( xa1 * ya )) - ( xa * yb1 )) 
    tb = float(b) / float(a)

    if (( tb <= 0 ) or ( tb >= 1 )):
        return None # doesn't intersect

    if ( xa == 0 ):
        if ( ya == 0 ):
            return None # you've confused a line with a point.
        ta = ( yb1 + ( yb * tb ) - ya1 ) / float(ya)
    else:
        ta = ( xb1 + ( xb * tb ) - xa1 ) / float(xa)

    if (( ta <= 0 ) or ( ta >= 1 )):
        return None # doesn't intersect
    
    x = xb1 + ( xb * tb )
    y = yb1 + ( yb * tb )
    return (x,y)



