#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pickle
from . import game_random, config, unit_test
from .primitives import *
from .game_types import *


def test_Config() -> None:
    """Test for config.py.

    Read, write and recreate the configuration file.
    Correctness is checked with assertions.
    """
    # Initial configuration
    test_screen = unit_test.Setup_For_Unit_Test()
    config.Initialise(True)     # full reinit
    assert config.cfg.mute
    assert config.cfg.version == VERSION
    assert config.cfg.test == 0
    assert config.FILENAME is not None

    # Configuration test
    config.cfg.test = 1
    config.Save()
    assert config.cfg.test == 1
    config.cfg.test = 2

    # Reload (test number goes back)
    config.Initialise(False)    # reload
    assert config.cfg.test == 1
    config.cfg.test = 3

    # Make invalid version (in a valid file)
    my_cfg = pickle.load(open(config.FILENAME, "rb"))
    my_cfg.version = "INVALID"
    pickle.dump(my_cfg, open(config.FILENAME, "wb"))
    config.Initialise(False)        # attempt to reload
    assert config.cfg.test == 3     # nothing was loaded
    assert config.cfg.version == VERSION

    # Make non-loadable configuration
    open(config.FILENAME, "wb").write(b"INVALID")
    config.Initialise(False)        # reload
    assert config.cfg.mute          # mute setting not reloaded (not loadable)
    assert config.cfg.test == 3     # nothing was loaded
    assert config.cfg.version == VERSION

    # Make non-saveable configuration
    copy = config.FILENAME
    config.FILENAME = None
    config.Save()                   # get exception handler coverage
    config.FILENAME = copy

    # Back to normal
    config.cfg.test = 0
    config.Initialise(True)

