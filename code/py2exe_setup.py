#!/usr/bin/env python

from distutils.core import setup

import py2exe , glob

setup(windows=[{"script": "../LightYears.py",
                "icon_resources": [(1,"..\\data\\32.ico")]}],
        data_files=[
            ("data", glob.glob("..\\data\\*.*")),
            ("data\\audio", glob.glob("..\\data\\audio\\*.*"))])


