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
                ".coverage", "code", "htmlcov",
                "data", "audio", "manual", "dist"])

    test = [sys.executable, "-m", "pytest", "--cov=code",
            "--cov-report=term:skip-covered",
            "--cov-report=html",
            "--no-cov-on-fail"]

    rc = subprocess.call([sys.executable, "-m", "mypy", "code", "lightyears"])
    if rc != 0:
        sys.exit(1)

    
    rc = subprocess.call(test + ["--cov-report="] +
                         sorted(glob.glob("code/*.py")))
    if rc != 0:
        sys.exit(1)

    rc = subprocess.call(test + ["--cov-append",
                         "--cov-report=term:skip-covered",
                         "--cov-report=html",
                         "run_all_tests.py"])
    if rc != 0:
        sys.exit(1)

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

def test_tutorial_die_2() -> None:
    run_a_test("tutorial_die_2")

def test_placement() -> None:
    run_a_test("placement")


if __name__ == "__main__":
    main()
