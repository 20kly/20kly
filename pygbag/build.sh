#!/bin/bash -xe

#git clean -d -f -x .

export ROOT=$PWD
export PYTHON=python3.11

$PYTHON -m venv build-env
source build-env/bin/activate

$PYTHON -m pip install pygbag==0.9.3
$PYTHON -m pip install pygame==2.6.1

# derive the version number
PYTHONPATH=$ROOT $PYTHON pyinstaller/linux/version_setup.py
source version.txt

# make the executable for the game
cd pygbag
rm -rf 20kly
mkdir 20kly
cd 20kly
cp -r $ROOT/lib20k $ROOT/data ../main.py .
cd ..
$PYTHON -m pygbag --app_name "20K Light Years" \
    --title "20K Light Years" \
    --version $VERSION \
    --no_opt --icon favicon.png \
    20kly
