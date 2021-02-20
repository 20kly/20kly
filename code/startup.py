# 
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
# 

# Version check. This file can be much shorter for Debian.

import sys 

def Check_Version():
    fault = False
    if ( sys.__dict__.get("version_info", None) ):
        (major, minor, micro, releaselevel, serial) = sys.version_info
        if (( major < 2 )
        or (( major == 2 ) and ( minor < 4 ))):
            fault = True
    else:
        major = 1
        minor = 0
        fault = True

    if ( fault ):
        print("")
        print("Python 2 version 2.4 or higher is required.")
        print("You appear to be using version",(str(major) + "." + str(minor)))
        sys.exit(1)
    
    try:
        import pygame
    except:
        print("")
        print("Pygame does not appear to be installed.")
        print("Please install the latest version from http://www.pygame.org/")
        sys.exit(1)
  
    try:
        # The size of this field changed between 
        # ver. 1.6 and ver. 1.7. Arrgh. 
        [major, minor] = list(pygame.version.vernum)[ 0:2 ]
        x = pygame.version.ver
    except:
        print("")
        print("Pygame is installed, but you have an old version.")
        print("Please install the latest version from http://www.pygame.org/")
        sys.exit(1)

    if (( major < 1 )
    or ( major == 1 ) and ( minor < 7 )):
        print("")
        print("Pygame version 1.7.x or higher is required.")
        print("Please install the latest version from http://www.pygame.org/")
        sys.exit(1)


def Get_Game_Version():
    return "1.3"

def Main(data_dir, ignore = None):
    Check_Version()
    import main
    main.Main(data_dir)


