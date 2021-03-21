#!/bin/bash -xe

rm -rf build dist
export ROOT=$PWD
pyinstaller -F pyinstaller/windows/lightyears.spec
/j/NSIS/makensis.exe //NOCD //WX pyinstaller/windows/nsis.nsi

