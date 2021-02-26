#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import subprocess
import sys
import os

def run_a_test(name: str) -> None:
    rc = subprocess.call([sys.executable, "lightyears",
                          "--playback", "tests/" + name])
    assert rc == 0, "Running " + name

def test_beginner() -> None:
    run_a_test("beginner")

def test_expert() -> None:
    run_a_test("expert")

def test_intermediate() -> None:
    run_a_test("intermediate")

def test_intermediate_die() -> None:
    run_a_test("intermediate_die")

def test_tutorial() -> None:
    run_a_test("tutorial")

def test_tutorial_die() -> None:
    run_a_test("tutorial_die")

def test_tutorial_die_2() -> None:
    run_a_test("tutorial_die_2")
