#!/bin/bash -xe

export LY=20kly-1.5.0
export ROOT=$PWD
export PYTHON=python3

# Build environment: pygame 2.0.1
rm -rf test-env build dist

$PYTHON -m venv test-env
source test-env/bin/activate

$PYTHON -m pip install pygame==2.0.1
$PYTHON -m pip install PyInstaller==4.2

pyinstaller -F pyinstaller/linux/lightyears.spec
cd dist
mkdir $LY
mv 20kly $LY
cp ../LICENSE.txt ../manual.pdf $LY
zip -9r $LY.zip $LY

