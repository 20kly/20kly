#!/usr/bin/python2.4
# Main program. Run this in order to play. Please see README.txt
# for more information.
# 
# Game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
#
# I hope you enjoy it. Have fun.

if ( __name__ == "__main__" ):
    import sys

    sys.path.insert(0, 'code')

    try:
        import startup
    except:
        print "Please run the program from the game directory."
        sys.exit(1)

    startup.Main()

