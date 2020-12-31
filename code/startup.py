# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-07.
# 

# Python version check. 2.4.x or higher is required.
# This also checks your Pygame version (after Python)
# Earlier versions *might* work but I haven't tested them...
# 2.4 is certainly required for built-in set() support.

import sys 

def Check_Version():
    fault = False
    if ( sys.__dict__.has_key("version_info" ) ):
        (major, minor, micro, releaselevel, serial) = sys.version_info
        if (( major < 2 )
        or (( major == 2 ) and ( minor < 4 ))):
            fault = True
    else:
        major = 1
        minor = 0
        fault = True

    if ( fault ):
        print ""
        print "Python version 2.4 or higher is required."
        print "You appear to be using version",(str(major) + "." + str(minor))
        print "Please install the latest version from http://www.python.org/"
        sys.exit(1)
    
    try:
        import pygame
    except:
        print ""
        print "Pygame does not appear to be installed."
        print "Please install the latest version from http://www.pygame.org/"
        sys.exit(1)
  
    try:
        # God damn! The size of this field changed between 
        # ver. 1.6 and ver. 1.7. Arrgh. 
        [major, minor] = list(pygame.version.vernum)[ 0:2 ]
        x = pygame.version.ver
    except:
        print ""
        print "Pygame is installed, but you have an old version."
        print "Please install the latest version from http://www.pygame.org/"
        sys.exit(1)

    if (( major < 1 )
    or ( major == 1 ) and ( minor < 7 )):
        print ""
        print "Pygame version 1.7.x or higher is required."
        print "Please install the latest version from http://www.pygame.org/"
        sys.exit(1)

    print "Python version",sys.version,"- good"
    print "Pygame version",pygame.version.ver,"- good"

def Get_Game_Version():
    # Used for savegames. Be sure to update this.
    return "1.3"

def Main(data_dir):
    print "Now checking your Python environment:"
    Check_Version()

    # Psyco is optional, but recommended :)
    if ( True ):
        try:
            import psyco
            psyco.profile()
        except Exception, r:
            print 'Psyco not found. If the game runs too slowly, '
            print 'install Psyco from http://psyco.sf.net/'

    import main

    print "Game booting - have fun!"
    main.Main(data_dir)


