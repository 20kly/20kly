#!/bin/bash -xe

git clean -d -f -x .

export PYTHON=/c/python38/python
export ROOT=$PWD

# derive the version number
PYTHONPATH=. $PYTHON pyinstaller/windows/version_setup.py

# make the .exe for the game
pyinstaller -F pyinstaller/windows/lightyears.spec

# make the .exe for the installer (skip if NSIS is not available)
/j/NSIS/makensis.exe //NOCD //WX pyinstaller/windows/nsis.nsi || true

# Test the version just built
dist/20kly.exe --playback tests/recordings/beginner

# Run all other tests
$PYTHON tests/run_all_tests.py
