#!/bin/bash
# 
# The management would like to apologise for not
# writing this script in Python. Note that you
# shouldn't need to run it.

sox bamboo.wav -t raw -u -b -r 11025 /tmp/hq
sox -t raw -u -b -r 17272 /tmp/hq /tmp/hq.wav
sox /tmp/hq.wav -r 22050 bamboo1.wav
sox -t raw -u -b -r 19692 /tmp/hq /tmp/hq.wav
sox /tmp/hq.wav -r 22050 bamboo2.wav




