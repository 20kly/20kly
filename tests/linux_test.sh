#!/bin/bash -xe

export PYTHON=python3

rm -rf test-env

$PYTHON -m venv test-env
source test-env/bin/activate

# Test with old Python 3.6 and old Pygame 1.9.6
# No mypy support here

$PYTHON -m pip install pygame==1.9.6
$PYTHON -m pip install pytest==6.2.2
$PYTHON -m pip install pytest-cov==2.11.1
$PYTHON tests/run_all_tests.py --no-mypy

