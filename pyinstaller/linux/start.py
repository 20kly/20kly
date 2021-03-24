import sys, os
from lib20k import Main, Events
data_dir = os.path.join(sys.prefix, "data")
Main(data_dir=data_dir, args=sys.argv[1:], event=Events())


