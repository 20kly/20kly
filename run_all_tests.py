#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#


import subprocess
import sys
import glob
import os
import getopt

def main() -> None:

    (opts_list, _) = getopt.getopt(
            sys.argv[1:], "", ["no-mypy", "no-clean", "no-full",
                               "no-coverage"])
    opts = dict(opts_list)

    clean = ["git", "clean", "-d", "-f", "-x"]
    test = [sys.executable, "-m", "pytest"]

    if "--no-clean" not in opts:
        subprocess.call(clean + ["code", "data", "audio", "manual", "dist"])

    if "--no-coverage" not in opts:
        subprocess.call(clean + [".coverage", "code", "htmlcov"])
        test += ["--cov=code", "--cov-append",
                "--cov-report=term:skip-covered",
                "--cov-report=html",
                "--no-cov-on-fail"]

    if "--no-mypy" not in opts:
        rc = subprocess.call([sys.executable,
                "-m", "mypy", "code", "lightyears"])
        if rc != 0:
            sys.exit(1)

    rc = subprocess.call(test + sorted(glob.glob("code/*.py")))
    if rc != 0:
        sys.exit(1)

    if "--no-full" not in opts:
        rc = subprocess.call(test + ["run_all_tests.py"])
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
