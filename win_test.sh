#!/bin/bash -e

PYTHON=/c/python38/python

# Test environment: python 3.8, pygame 2.0.1, 32-bit (development platform)
$PYTHON run_all_tests.py

PYTHON=/c/python39/python

# Test environment: python 3.9, pygame 2.0.1, 64-bit
rm -rf test-env

$PYTHON -m venv test-env
source test-env/Scripts/activate

$PYTHON -m pip install pygame==2.0.1
$PYTHON -m pip install pytest==6.2.2
$PYTHON run_all_tests.py --no-mypy --no-coverage

