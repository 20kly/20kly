#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#
# The recommended way to run the tests on Linux is
# 1. apt-get install python3-pytest-cov xvfb
# 2. xvfb-run python tests/run_all_tests.py

import subprocess
import sys
import glob
import os
import getopt
import typing

clean = ["git", "clean", "-d", "-f", "-x"]

def main() -> None:

    try:
        (opts_list, _) = getopt.getopt(
            sys.argv[1:], "", ["no-mypy", "no-clean", "no-full",
                               "no-coverage"])
    except getopt.GetoptError as e:
        print(e)
        print("""
Options:
    --no-mypy       Disable mypy check
    --no-clean      Disable git clean step
    --no-full       Disable higher resolution video tests
    --no-coverage   Disable coverage check
""")
        sys.exit(1)

    opts = dict(opts_list)

    test = [sys.executable, "-m", "pytest"]

    # Check test dependencies are installed: pytest
    if 0 != subprocess.call(test + ["--version"], stdout=subprocess.DEVNULL):
        print("pytest >= 6.2.2 is required")
        sys.exit(1)

    # pytest-cov plugin
    if ("--no-coverage" not in opts) and (0 != subprocess.call(test + ["--cov", "--version"], stdout=subprocess.DEVNULL)):
        print("pytest-cov >= 2.11.1 is required (or use --no-coverage)")
        sys.exit(1)

    # Running in correct directory?
    if not (os.path.isfile("tests/run_all_tests.py")
            and os.path.isdir(".git")
            and os.path.isfile("lib20ktest/__init__.py")):
        print("Please start the test program from the lightyears root directory")
        sys.exit(1)

    if "--no-clean" not in opts:
        subprocess.call(clean + ["lib20k", "lib20ktest", "data", "tmp"])

    if not os.path.isdir("tmp"):
        os.mkdir("tmp")
    os.environ["HOME"] = os.path.abspath("tmp")

    if "--no-coverage" not in opts:
        subprocess.call(clean + [".coverage", "htmlcov"])
        test += ["--cov=lib20k", "--cov-append",
                "--cov-report=term:skip-covered",
                "--cov-report=html",
                "--no-cov-on-fail"]

    if "--no-mypy" not in opts:
        rc = subprocess.call([sys.executable,
                "-m", "mypy", "lib20k", "lib20ktest", "lightyears"])
        if rc != 0:
            print("failed: mypy tests")
            sys.exit(1)

    rc = subprocess.call(test + sorted(glob.glob("lib20ktest/test_*.py")))
    if rc != 0:
        print("failed: unit tests")
        sys.exit(1)

    if "--no-full" not in opts:
        # 4K tests run separately (stability problems on Ubuntu 18.04)
        rc = subprocess.call(test + sorted(glob.glob("lib20ktest/4k_test_*.py")))
        if rc != 0:
            print("failed: 4k test")
            sys.exit(1)

        # Regression tests run separately
        rc = subprocess.call(test + ["-v", "tests/run_all_tests.py"])
        if rc != 0:
            print("failed: regression tests")
            sys.exit(1)

def run_a_test(name: str, args: typing.List[str] = []) -> None:
    rc = subprocess.call([sys.executable, "lightyears",
                          "--playback", "tests/recordings/" + name] + args)
    assert rc == 0, "Running " + name

def test_shots1K() -> None:
    run_a_test("shots", ["--test-height=1000"])
    subprocess.call(clean + ["tmp/.lightyears.cfg"])

def test_shots4K() -> None:
    run_a_test("shots", ["--test-height=4000"])
    subprocess.call(clean + ["tmp/.lightyears.cfg"])

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
