
from lib20k.primitives import VERSION

open("version.txt", "wt", encoding="utf-8").write(
    "VERSION={}.{}.{}\n".format(*VERSION))

