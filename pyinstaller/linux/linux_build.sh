#!/bin/bash -xe

git clean -d -f -x .

export ROOT=$PWD
export PYTHON=python3.8

# Build environment: pygame 2.0.1
$PYTHON -m venv test-env
source test-env/bin/activate

$PYTHON -m pip install wheel==0.36.2
$PYTHON -m pip install pygame==2.0.1
$PYTHON -m pip install PyInstaller==4.2
$PYTHON -m pip install mypy==0.812
$PYTHON -m pip install pytest==6.2.2
$PYTHON -m pip install pytest-cov==2.11.1

# derive the version number
PYTHONPATH=$ROOT $PYTHON pyinstaller/linux/version_setup.py
source version.txt
export LY=20kly-$VERSION

# make the executable for the game
pyinstaller -F pyinstaller/linux/lightyears.spec

# make the zip file
cd dist
mkdir $LY
cp 20kly $LY
cp ../LICENSE.txt ../manual.pdf $LY
zip -9r $LY.zip $LY
cd ..

# Test the version just built
dist/20kly --playback tests/recordings/beginner

# Run all other tests
$PYTHON tests/run_all_tests.py
