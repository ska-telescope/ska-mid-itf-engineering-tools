#!/usr/bin/python
"""
Read wheel file
"""
import sys
from zipfile import ZipFile

try:
    fpath: str = sys.argv[1]
except IndexError:
    print(f"Usage {sys.argv[0]} <WHEEL>")
    sys.exit(1)
names: list = ZipFile(fpath).namelist()
print(f"Wheel {fpath}")
for name in names:
    print(f"\t{name}")
