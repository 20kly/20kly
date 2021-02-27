#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import subprocess
import sys
import glob
import os

def main() -> None:
    rc = subprocess.call([sys.executable, "-m", "mypy", "code", "lightyears"])
    if rc != 0:
        sys.exit(1)

    rc = subprocess.call([sys.executable, "-m", "pytest"] +
                         sorted(glob.glob("code/*.py")) +
                         ["tests/regression_test.py"])
    if rc != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
