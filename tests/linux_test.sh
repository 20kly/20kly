#!/bin/bash -e

export PYTHON=python3

# Test environment: pygame 2.0.1
rm -rf test-env

$PYTHON -m venv test-env
source test-env/bin/activate

$PYTHON -m pip install pygame==2.0.1
$PYTHON -m pip install mypy==0.812
$PYTHON -m pip install pytest==6.2.2
$PYTHON -m pip install pytest-cov==2.11.1
$PYTHON tests/run_all_tests.py --no-coverage

# Switch to old pygame version 1.9.6
# No mypy support here

$PYTHON -m pip uninstall -y pygame
$PYTHON -m pip install pygame==1.9.6
$PYTHON tests/run_all_tests.py --no-mypy

