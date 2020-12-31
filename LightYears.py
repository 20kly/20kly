#!/usr/bin/python2.4
# Main program. Run this in order to play. Please see README.txt
# for more information.
# 
# Game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
#
# I hope you enjoy it. Have fun.

if ( __name__ == "__main__" ):
    import sys, os

    CODE_DIR = os.path.abspath(os.path.join(
                os.path.dirname(sys.argv[ 0 ]), "code"))

    sys.path.insert(0, CODE_DIR)

    try:
        import startup
    except:
        print "Unable to find programs - searched", CODE_DIR
        sys.exit(1)

    startup.Main()

