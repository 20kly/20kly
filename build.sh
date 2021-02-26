#!/bin/bash -xe


python -m mypy code/*.py
python -m pytest code/*.py

export L="python lightyears --playback"
$L tests/tutorial_die
$L tests/tutorial_die_2
$L tests/beginner
$L tests/tutorial
$L tests/intermediate
$L tests/intermediate_die
$L tests/expert

echo "Tests ok"

