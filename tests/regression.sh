#!/bin/bash -xe

export L="python lightyears --playback"

$L tests/tutorial_die
$L tests/tutorial_die_2
$L tests/beginner
$L tests/tutorial

echo "Tests ok"

