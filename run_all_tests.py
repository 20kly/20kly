#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import subprocess
import sys
import glob
import os

def main() -> None:

    subprocess.call(["git", "clean", "-d", "-f", "-x",
                "code",
                "data", "audio", "manual", "dist"])

    test = [sys.executable, "-m", "pytest"]
    rc = subprocess.call(test + ["run_all_tests.py"])
    if rc != 0:
        sys.exit(1)

def run_a_test(name: str) -> None:
    run = [sys.executable, "lightyears"]
    if os.path.isfile("20kly.exe"):
        run = ["20kly.exe"]
    rc = subprocess.call(run + ["--playback", "tests/" + name])
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

def test_tutorial_die_2() -> None:
    run_a_test("tutorial_die_2")

def test_placement() -> None:
    run_a_test("placement")


if __name__ == "__main__":
    main()
